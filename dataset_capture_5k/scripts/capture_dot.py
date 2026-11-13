"""
Automated Capture for Class: DOT (DNS-over-TLS, RFC 7858).
Captures 5,000 packets across genuine DoT endpoints on TCP 853.
"""

import socket
import ssl
import threading
import time
from pathlib import Path
from typing import List, Tuple
from common import REAL_DOMAINS, build_dns_query_wire, save_packets_to_pcap

DOT_ENDPOINTS = [
    ("1.1.1.1", 853, "cloudflare-dns.com"),
    ("8.8.8.8", 853, "dns.google"),
    ("9.9.9.9", 853, "dns.quad9.net"),
    ("94.140.14.14", 853, "dns.adguard-dns.com"),
]


def capture_dot_session(
    remote_ip: str,
    remote_port: int,
    server_hostname: str,
    domains: List[str],
    output_pcap: str,
    local_port: int = 21853
) -> int:
    raw_events: List[Tuple[str, float, bytes]] = []
    relay_ready = threading.Event()
    stop_relay = threading.Event()

    def relay_server():
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", local_port))
        srv.listen(1)
        srv.settimeout(12.0)
        relay_ready.set()

        try:
            client_conn, client_addr = srv.accept()
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
            t1.join(timeout=15.0)
            t2.join(timeout=15.0)
        except Exception:
            pass
        finally:
            srv.close()

    th = threading.Thread(target=relay_server)
    th.start()
    relay_ready.wait(timeout=5.0)
    time.sleep(0.05)

    try:
        s = socket.create_connection(("127.0.0.1", local_port), timeout=10.0)
        ctx = ssl.create_default_context()
        tls_s = ctx.wrap_socket(s, server_hostname=server_hostname)

        for domain in domains:
            dns_wire = build_dns_query_wire(domain)
            dot_payload = len(dns_wire).to_bytes(2, "big") + dns_wire
            tls_s.sendall(dot_payload)
            try:
                resp = tls_s.recv(4096)
            except Exception:
                pass
            time.sleep(0.01)

        tls_s.close()
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


def run_dot_capture(target_samples: int = 5000, output_dir: str = "captures/DOT"):
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    total_pkts = 0
    session_idx = 1

    print(f"[*] Starting legitimate DoT capture targeting ~{target_samples:,} packets...")
    while total_pkts < target_samples:
        endpoint = DOT_ENDPOINTS[session_idx % len(DOT_ENDPOINTS)]
        pcap_file = out_path / f"dot_session_{session_idx:04d}.pcap"
        domains_batch = [REAL_DOMAINS[(session_idx * 7 + i) % len(REAL_DOMAINS)] for i in range(50)]

        pkts = capture_dot_session(
            remote_ip=endpoint[0],
            remote_port=endpoint[1],
            server_hostname=endpoint[2],
            domains=domains_batch,
            output_pcap=str(pcap_file),
            local_port=21853 + (session_idx % 200)
        )
        total_pkts += pkts
        print(f"  [DoT Session {session_idx}] Endpoint: {endpoint[2]} -> {pkts} pkts (Cumulative: {total_pkts}/{target_samples})")
        session_idx += 1
        time.sleep(0.05)

    print(f"[+] DoT capture completed: {total_pkts:,} packets saved in {session_idx-1} PCAP files.")
    return total_pkts


if __name__ == "__main__":
    run_dot_capture(5000)

