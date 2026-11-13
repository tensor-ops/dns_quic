"""
Automated Capture for Class: DOQ (DNS-over-QUIC, RFC 9250).
Captures 5,000 packets across genuine DoQ endpoints on UDP 853.
"""

import asyncio
from pathlib import Path
import time
from typing import List, Tuple
from aioquic.asyncio.client import connect
from aioquic.quic.configuration import QuicConfiguration
from common import REAL_DOMAINS, build_dns_query_wire, save_packets_to_pcap

DOQ_ENDPOINTS = [
    ("94.140.14.14", 853, "dns.adguard-dns.com"),
    ("94.140.15.15", 853, "dns-family.adguard-dns.com"),
]


async def capture_doq_session_async(
    remote_ip: str,
    remote_port: int,
    server_hostname: str,
    domains: List[str],
    output_pcap: str,
) -> int:
    raw_events: List[Tuple[str, float, bytes]] = []

    config = QuicConfiguration(
        is_client=True,
        alpn_protocols=["doq"],
        server_name=server_hostname,
        verify_mode=False
    )

    try:
        async with connect(remote_ip, remote_port, configuration=config) as proto:
            orig_sendto = proto._transport.sendto
            def wrapped_sendto(data, *args):
                raw_events.append(("upstream", time.time(), data))
                return orig_sendto(data, *args)
            proto._transport.sendto = wrapped_sendto

            orig_datagram_received = proto.datagram_received
            def wrapped_datagram_received(data, addr):
                raw_events.append(("downstream", time.time(), data))
                return orig_datagram_received(data, addr)
            proto.datagram_received = wrapped_datagram_received

            for domain in domains:
                dns_wire = build_dns_query_wire(domain)
                doq_msg = len(dns_wire).to_bytes(2, "big") + dns_wire
                stream_id = proto._quic.get_next_available_stream_id()
                proto._quic.send_stream_data(stream_id, doq_msg, end_stream=True)
                proto.transmit()
                await asyncio.sleep(0.02)

            await asyncio.sleep(0.4)
    except Exception:
        pass

    return save_packets_to_pcap(
        raw_events,
        client_ip="172.17.246.115",
        client_port=56853,
        remote_ip=remote_ip,
        remote_port=remote_port,
        proto="UDP",
        output_pcap=output_pcap
    )


def run_doq_capture(target_samples: int = 5000, output_dir: str = "captures/DOQ"):
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    total_pkts = 0
    session_idx = 1

    print(f"[*] Starting legitimate DoQ capture targeting ~{target_samples:,} packets...")
    while total_pkts < target_samples:
        endpoint = DOQ_ENDPOINTS[session_idx % len(DOQ_ENDPOINTS)]
        pcap_file = out_path / f"doq_session_{session_idx:04d}.pcap"
        domains_batch = [REAL_DOMAINS[(session_idx * 7 + i) % len(REAL_DOMAINS)] for i in range(60)]

        pkts = asyncio.run(
            capture_doq_session_async(
                remote_ip=endpoint[0],
                remote_port=endpoint[1],
                server_hostname=endpoint[2],
                domains=domains_batch,
                output_pcap=str(pcap_file)
            )
        )
        total_pkts += pkts
        print(f"  [DoQ Session {session_idx}] Endpoint: {endpoint[2]} -> {pkts} pkts (Cumulative: {total_pkts}/{target_samples})")
        session_idx += 1
        time.sleep(0.05)

    print(f"[+] DoQ capture completed: {total_pkts:,} packets saved in {session_idx-1} PCAP files.")
    return total_pkts


if __name__ == "__main__":
    run_doq_capture(5000)

