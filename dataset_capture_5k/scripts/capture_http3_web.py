"""
Automated Capture for Class: HTTP3_WEB (Modern Encrypted Web Traffic over QUIC).
Captures 5,000 packets across genuine public HTTP/3 servers on UDP 443.
"""

import asyncio
from pathlib import Path
import time
from typing import List, Tuple
from aioquic.asyncio.client import connect
from aioquic.quic.configuration import QuicConfiguration
from aioquic.h3.connection import H3Connection
from aioquic.h3.events import DataReceived, HeadersReceived
from common import save_packets_to_pcap

HTTP3_TARGETS = [
    ("cloudflare.com", "104.16.132.229", ["/", "/learning/", "/plans/"]),
    ("google.com", "142.250.190.46", ["/", "/search?q=dns+quic", "/search?q=encrypted+dns"]),
    ("facebook.com", "157.240.241.35", ["/", "/login/", "/help"]),
]


async def capture_http3_web_session_async(
    hostname: str,
    ip_addr: str,
    paths: List[str],
    output_pcap: str,
) -> int:
    raw_events: List[Tuple[str, float, bytes]] = []

    config = QuicConfiguration(
        is_client=True,
        alpn_protocols=["h3", "h3-29"],
        server_name=hostname,
        verify_mode=False
    )

    try:
        async with connect(ip_addr, 443, configuration=config) as proto:
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

            for path in paths:
                stream_id = proto._quic.get_next_available_stream_id()
                headers = [
                    (b":method", b"GET"),
                    (b":scheme", b"https"),
                    (b":authority", hostname.encode("ascii")),
                    (b":path", path.encode("ascii")),
                    (b"user-agent", b"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0"),
                ]
                h3_conn.send_headers(stream_id=stream_id, headers=headers, end_stream=True)
                proto.transmit()
                await asyncio.sleep(0.05)

            await asyncio.sleep(0.4)
    except Exception:
        pass

    return save_packets_to_pcap(
        raw_events,
        client_ip="172.17.246.115",
        client_port=56444,
        remote_ip=ip_addr,
        remote_port=443,
        proto="UDP",
        output_pcap=output_pcap
    )


def run_http3_web_capture(target_samples: int = 5000, output_dir: str = "captures/HTTP3_WEB"):
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    total_pkts = 0
    session_idx = 1

    print(f"[*] Starting legitimate HTTP3_WEB capture targeting ~{target_samples:,} packets...")
    while total_pkts < target_samples:
        target = HTTP3_TARGETS[session_idx % len(HTTP3_TARGETS)]
        pcap_file = out_path / f"http3_web_session_{session_idx:04d}.pcap"

        pkts = asyncio.run(
            capture_http3_web_session_async(
                hostname=target[0],
                ip_addr=target[1],
                paths=target[2],
                output_pcap=str(pcap_file)
            )
        )
        total_pkts += pkts
        print(f"  [HTTP3_WEB Session {session_idx}] Target: {target[0]} -> {pkts} pkts (Cumulative: {total_pkts}/{target_samples})")
        session_idx += 1
        time.sleep(0.05)

    print(f"[+] HTTP3_WEB capture completed: {total_pkts:,} packets saved in {session_idx-1} PCAP files.")
    return total_pkts


if __name__ == "__main__":
    run_http3_web_capture(5000)

