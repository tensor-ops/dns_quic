"""
Automated Capture for Class: DOH (DNS-over-HTTPS, RFC 8484).
Captures 5,000 packets across genuine DoH endpoints on TCP 443.
"""

import base64
import socket
import ssl
import threading
import time
from pathlib import Path
from typing import List, Tuple
import httpx
from common import REAL_DOMAINS, build_dns_query_wire, save_packets_to_pcap

DOH_ENDPOINTS = [
    ("1.1.1.1", 443, "cloudflare-dns.com", "/dns-query"),
    ("8.8.8.8", 443, "dns.google", "/dns-query"),
    ("9.9.9.9", 443, "dns.quad9.net", "/dns-query"),
    ("94.140.14.14", 443, "dns.adguard-dns.com", "/dns-query"),
]


def capture_doh_session(
    remote_ip: str,
    remote_port: int,
    server_hostname: str,
    endpoint_path: str,
    domains: List[str],
    output_pcap: str,
    local_port: int = 21443
) -> int:
    raw_events: List[Tuple[str, float, bytes]] = []
    relay_ready = threading.Event()
    stop_relay = threading.Event()

    def relay_server():
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", local_port))
        srv.listen(5)
        srv.settimeout(12.0)
        relay_ready.set()

        try:
            while not stop_relay.is_set():
                try:
                    client_conn, _ = srv.accept()
                except socket.timeout:
                    continue
                upstream_conn = socket.create_connection((remote_ip, remote_port), timeout=10.0)

                def forward(src, dst, direction):
                    src.settimeout(2.0)
                    while not stop_relay.is_set():
                        try:
                            data = src.recv(8192)
                            if not data:
                                break
                            raw_events.append((direction, time.time(), data))
                            dst.sendall(data)
                        except socket.timeout:
                            continue
                        except Exception:
                            break
                    src.close()
                    dst.close()

                t1 = threading.Thread(target=forward, args=(client_conn, upstream_conn, "upstream"))
                t2 = threading.Thread(target=forward, args=(upstream_conn, client_conn, "downstream"))
                t1.start()
                t2.start()
        except Exception:
            pass
        finally:
            srv.close()

    th = threading.Thread(target=relay_server)
    th.start()
    relay_ready.wait(timeout=5.0)
    time.sleep(0.05)

    try:
        with httpx.Client(
            base_url=f"https://{server_hostname}",
            verify=False,
            http2=True,
            timeout=10.0
        ) as client:
            for domain in domains:
                dns_wire = build_dns_query_wire(domain)
                try:
                    resp = httpx.post(
                        f"https://127.0.0.1:{local_port}{endpoint_path}",
                        headers={
                            "Host": server_hostname,
                            "Content-Type": "application/dns-message",
                            "Accept": "application/dns-message",
                        },
                        content=dns_wire,
                        verify=False,
                        timeout=5.0
                    )
                except Exception:
                    pass
                time.sleep(0.01)
    except Exception:
        pass
    finally:
        stop_relay.set()
        th.join(timeout=3.0)

    return save_packets_to_pcap(
        raw_events,
        client_ip="172.17.246.115",
        client_port=local_port,
        remote_ip=remote_ip,
        remote_port=remote_port,
        proto="TCP",
        output_pcap=output_pcap
    )


def run_doh_capture(target_samples: int = 5000, output_dir: str = "captures/DOH"):
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    total_pkts = 0
    session_idx = 1

    print(f"[*] Starting legitimate DoH capture targeting ~{target_samples:,} packets...")
    while total_pkts < target_samples:
        endpoint = DOH_ENDPOINTS[session_idx % len(DOH_ENDPOINTS)]
        pcap_file = out_path / f"doh_session_{session_idx:04d}.pcap"
        domains_batch = [REAL_DOMAINS[(session_idx * 7 + i) % len(REAL_DOMAINS)] for i in range(50)]

        pkts = capture_doh_session(
            remote_ip=endpoint[0],
            remote_port=endpoint[1],
            server_hostname=endpoint[2],
            endpoint_path=endpoint[3],
            domains=domains_batch,
            output_pcap=str(pcap_file),
            local_port=21443 + (session_idx % 200)
        )
        total_pkts += pkts
        print(f"  [DoH Session {session_idx}] Endpoint: {endpoint[2]} -> {pkts} pkts (Cumulative: {total_pkts}/{target_samples})")
        session_idx += 1
        time.sleep(0.05)

    print(f"[+] DoH capture completed: {total_pkts:,} packets saved in {session_idx-1} PCAP files.")
    return total_pkts


if __name__ == "__main__":
    run_doh_capture(5000)

