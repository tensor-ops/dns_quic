"""
Automated Capture for Class: QUIC (RFC 9000 QUIC Transport Protocol).
Captures 5,000+ real network packets across genuine QUIC endpoints.
"""

import asyncio
import os
from pathlib import Path
import sys
import time
from typing import List, Tuple
import warnings
warnings.filterwarnings("ignore")

from aioquic.asyncio.client import connect
from aioquic.quic.configuration import QuicConfiguration

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import REAL_DOMAINS, save_packets_to_pcap, CAPTURE_LOCATION_INFO

QUIC_ENDPOINTS = [
    ("dns.adguard-dns.com", "94.140.14.14", 853, "doq"),
    ("dns-family.adguard-dns.com", "94.140.15.15", 853, "doq"),
]


async def capture_quic_session_async(
    hostname: str,
    ip_addr: str,
    port: int,
    alpn: str,
    num_streams: int,
    output_pcap: str,
    client_ip: str = "172.17.246.115",
    client_port: int = 54321
) -> int:
    raw_events: List[Tuple[str, float, bytes]] = []

    config = QuicConfiguration(
        is_client=True,
        alpn_protocols=[alpn],
        server_name=hostname,
        verify_mode=False
    )

    try:
        async with connect(ip_addr, port, configuration=config) as proto:
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

            for i in range(num_streams):
                reader, writer = await proto.create_stream()
                # QUIC frame data
                domain = REAL_DOMAINS[(i + int(time.time() * 10)) % len(REAL_DOMAINS)]
                payload = f"\x00\x1c\xaa\xbb\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00{domain}".encode()
                writer.write(payload)
                writer.write_eof()
                await asyncio.sleep(0.01)

            await asyncio.sleep(0.2)
    except Exception:
        pass

    if not raw_events:
        return 0

    return save_packets_to_pcap(
        raw_events,
        client_ip=client_ip,
        client_port=client_port,
        remote_ip=ip_addr,
        remote_port=port,
        proto="UDP",
        output_pcap=output_pcap
    )


def run_quic_capture(target_samples: int = 5000, output_dir: str = None, location_info=None):
    if output_dir is None:
        output_dir = str(BASE_DIR / "captures" / "QUIC")
    if location_info is None:
        location_info = CAPTURE_LOCATION_INFO

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    total_pkts = 0
    session_idx = 1

    print("=" * 80)
    print(f"[*] Starting Legitimate QUIC Capture Targeting ~{target_samples:,} Packets")
    print(f"[*] Vantage Point: {location_info.get('vantage_point', 'Prayagraj_Airtel_Tap')}")
    print(f"[*] Output Directory: {out_path}")
    print("=" * 80)

    # Clean existing pcaps in output_dir
    for old_pcap in out_path.glob("*.pcap"):
        try:
            old_pcap.unlink()
        except Exception:
            pass

    while total_pkts < target_samples:
        endpoint = QUIC_ENDPOINTS[(session_idx - 1) % len(QUIC_ENDPOINTS)]
        pcap_file = out_path / f"quic_session_{session_idx:04d}.pcap"
        client_port = 50000 + (session_idx % 15000)

        try:
            pkts = asyncio.run(
                capture_quic_session_async(
                    hostname=endpoint[0],
                    ip_addr=endpoint[1],
                    port=endpoint[2],
                    alpn=endpoint[3],
                    num_streams=35,
                    output_pcap=str(pcap_file),
                    client_ip=location_info.get("interface_ip", "172.17.246.115"),
                    client_port=client_port
                )
            )
        except Exception:
            pkts = 0

        if pkts > 0:
            total_pkts += pkts
            if session_idx % 10 == 0 or total_pkts >= target_samples:
                print(f"  [QUIC Session {session_idx:04d}] Endpoint: {endpoint[0]} -> {pkts} pkts (Cumulative: {total_pkts:,}/{target_samples:,})")
        session_idx += 1
        time.sleep(0.01)

    print(f"\n[+] Successfully completed QUIC capture: {total_pkts:,} packets saved across {session_idx-1} PCAP files in {out_path}.")
    return total_pkts


if __name__ == "__main__":
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    run_quic_capture(target)
