"""
Automated Capture for Class: HTTPS_WEB (Ordinary Encrypted Web Traffic).
Captures 5,000 packets across diverse public HTTPS websites on TCP 443.
"""

import socket
import ssl
import threading
import time
from pathlib import Path
from typing import List, Tuple
import httpx
from common import save_packets_to_pcap

WEB_TARGETS = [
    ("cloudflare.com", "104.16.132.229", ["/", "/learning/", "/plans/"]),
    ("wikipedia.org", "208.80.154.224", ["/", "/wiki/Main_Page", "/wiki/Special:Search"]),
    ("python.org", "151.101.128.223", ["/", "/downloads/", "/doc/"]),
    ("github.com", "140.82.112.4", ["/", "/features", "/explore"]),
    ("mozilla.org", "151.101.128.167", ["/", "/en-US/firefox/", "/en-US/about/"]),
    ("apache.org", "151.101.65.172", ["/", "/foundation/", "/licenses/"]),
]


def capture_https_web_session(
    hostname: str,
    ip_addr: str,
    paths: List[str],
    output_pcap: str,
    local_port: int = 21444
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
                upstream_conn = socket.create_connection((ip_addr, 443), timeout=10.0)

                def forward(src, dst, direction):
                    src.settimeout(2.0)
                    while not stop_relay.is_set():
                        try:
                            data = src.recv(16384)
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
        for path in paths:
            try:
                resp = httpx.get(
                    f"https://127.0.0.1:{local_port}{path}",
                    headers={"Host": hostname, "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0"},
                    verify=False,
                    timeout=6.0
                )
            except Exception:
                pass
            time.sleep(0.02)
    except Exception:
        pass
    finally:
        stop_relay.set()
        th.join(timeout=3.0)

    return save_packets_to_pcap(
        raw_events,
        client_ip="172.17.246.115",
        client_port=local_port,
        remote_ip=ip_addr,
        remote_port=443,
        proto="TCP",
        output_pcap=output_pcap
    )


def run_https_web_capture(target_samples: int = 5000, output_dir: str = "captures/HTTPS_WEB"):
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    total_pkts = 0
    session_idx = 1

    print(f"[*] Starting legitimate HTTPS_WEB capture targeting ~{target_samples:,} packets...")
    while total_pkts < target_samples:
        target = WEB_TARGETS[session_idx % len(WEB_TARGETS)]
        pcap_file = out_path / f"https_web_session_{session_idx:04d}.pcap"

        pkts = capture_https_web_session(
            hostname=target[0],
            ip_addr=target[1],
            paths=target[2],
            output_pcap=str(pcap_file),
            local_port=21444 + (session_idx % 200)
        )
        total_pkts += pkts
        print(f"  [HTTPS_WEB Session {session_idx}] Target: {target[0]} -> {pkts} pkts (Cumulative: {total_pkts}/{target_samples})")
        session_idx += 1
        time.sleep(0.05)

    print(f"[+] HTTPS_WEB capture completed: {total_pkts:,} packets saved in {session_idx-1} PCAP files.")
    return total_pkts


if __name__ == "__main__":
    run_https_web_capture(5000)

