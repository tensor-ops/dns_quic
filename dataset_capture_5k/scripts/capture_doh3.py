"""
Automated Capture for Class: DOH3 (DNS-over-HTTP/3, RFC 9114).
Captures 5,000 packets across genuine DoH/3 endpoints on UDP 443.
"""

import asyncio
import base64
from pathlib import Path
import time
from typing import List, Tuple
from aioquic.asyncio.client import connect
from aioquic.quic.configuration import QuicConfiguration
from aioquic.h3.connection import H3Connection
from aioquic.h3.events import DataReceived, HeadersReceived
from common import REAL_DOMAINS, build_dns_query_wire, save_packets_to_pcap

DOH3_ENDPOINTS = [
    ("1.1.1.1", 443, "cloudflare-dns.com", "/dns-query"),
    ("8.8.8.8", 443, "dns.google", "/dns-query"),
]


async def capture_doh3_session_async(
    remote_ip: str,
    remote_port: int,
    server_hostname: str,
    endpoint_path: str,
    domains: List[str],
    output_pcap: str,
) -> int:
    raw_events: List[Tuple[str, float, bytes]] = []

    config = QuicConfiguration(
        is_client=True,
        alpn_protocols=["h3", "h3-29"],
        server_name=server_hostname,
        verify_mode=False
    )

    try:
        async with connect(remote_ip, remote_port, configuration=config) as proto:
            h3_conn = H3Connection(proto._quic)

            orig_sendto = proto._transport.sendto
            def wrapped_sendto(data, *args):
                raw_events.append(("upstream", time.time(), data))
                return orig_sendto(data, *args)
            proto._transport.sendto = wrapped_sendto

            orig_datagram_received = proto.datagram_received
            def wrapped_datagram_received(data, addr):
                raw_events.append(("downstream", time.time(), data))
                orig_datagram_received(data, addr)
                while True:
                    event = proto._quic.next_event()
                    if event is None:
                        break
                    h3_conn.handle_event(event)
            proto.datagram_received = wrapped_datagram_received

            proto.transmit()
            await asyncio.sleep(0.05)

            for domain in domains:
                dns_wire = build_dns_query_wire(domain)
                b64_query = base64.urlsafe_b64encode(dns_wire).decode("ascii").rstrip("=")
                stream_id = proto._quic.get_next_available_stream_id()

                headers = [
                    (b":method", b"GET"),
                    (b":scheme", b"https"),
                    (b":authority", server_hostname.encode("ascii")),
                    (b":path", f"{endpoint_path}?dns={b64_query}".encode("ascii")),
                    (b"accept", b"application/dns-message"),
                ]
                h3_conn.send_headers(stream_id=stream_id, headers=headers, end_stream=True)
                proto.transmit()
                await asyncio.sleep(0.02)

            await asyncio.sleep(0.4)
    except Exception:
        pass

    return save_packets_to_pcap(
        raw_events,
        client_ip="172.17.246.115",
        client_port=56443,
        remote_ip=remote_ip,
        remote_port=remote_port,
        proto="UDP",
        output_pcap=output_pcap
    )


def run_doh3_capture(target_samples: int = 5000, output_dir: str = "captures/DOH3"):
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    total_pkts = 0
    session_idx = 1

    print(f"[*] Starting legitimate DoH3 capture targeting ~{target_samples:,} packets...")
    while total_pkts < target_samples:
        endpoint = DOH3_ENDPOINTS[session_idx % len(DOH3_ENDPOINTS)]
        pcap_file = out_path / f"doh3_session_{session_idx:04d}.pcap"
        domains_batch = [REAL_DOMAINS[(session_idx * 7 + i) % len(REAL_DOMAINS)] for i in range(60)]

        pkts = asyncio.run(
            capture_doh3_session_async(
                remote_ip=endpoint[0],
                remote_port=endpoint[1],
                server_hostname=endpoint[2],
                endpoint_path=endpoint[3],
                domains=domains_batch,
                output_pcap=str(pcap_file)
            )
        )
        total_pkts += pkts
        print(f"  [DoH3 Session {session_idx}] Endpoint: {endpoint[2]} -> {pkts} pkts (Cumulative: {total_pkts}/{target_samples})")
        session_idx += 1
        time.sleep(0.05)

    print(f"[+] DoH3 capture completed: {total_pkts:,} packets saved in {session_idx-1} PCAP files.")
    return total_pkts


if __name__ == "__main__":
    run_doh3_capture(5000)

