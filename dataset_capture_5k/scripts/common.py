"""
Common utilities, domain lists, network location metadata, and PCAP writer helpers.
"""

from pathlib import Path
import random
import time
from typing import List, Tuple
from scapy.layers.inet import IP, TCP, UDP
import scapy.all as scapy

# Location metadata where packets are captured
CAPTURE_LOCATION_INFO = {
    "network_id": "AIRTEL_PRAYAGRAJ_LAB",
    "interface": "en0",
    "interface_ip": "172.17.246.115",
    "public_ip": "223.189.244.49",
    "isp": "Bharti Airtel Ltd. (AS45609)",
    "subnet": "172.17.246.0/24",
    "vantage_point": "Prayagraj_Airtel_Tap",
    "city": "Prayagraj",
    "state": "Uttar Pradesh",
    "country": "India",
    "geolocation": "Prayagraj, Uttar Pradesh, India (Asia/Kolkata UTC+05:30)"
}

REAL_DOMAINS = [
    "google.com", "youtube.com", "facebook.com", "wikipedia.org", "twitter.com",
    "amazon.com", "apple.com", "microsoft.com", "reddit.com", "netflix.com",
    "linkedin.com", "instagram.com", "github.com", "cloudflare.com", "mozilla.org",
    "wordpress.org", "adobe.com", "zoom.us", "dropbox.com", "spotify.com",
    "cnn.com", "bbc.co.uk", "nytimes.com", "medium.com", "stackoverflow.com",
    "imdb.com", "quora.com", "office.com", "bing.com", "live.com",
    "pinterest.com", "twitch.tv", "paypal.com", "salesforce.com", "vimeo.com",
    "craigslist.org", "chase.com", "wellsfargo.com", "bankofamerica.com", "walmart.com",
    "target.com", "ebay.com", "etsy.com", "yelp.com", "booking.com",
    "tripadvisor.com", "airbnb.com", "uber.com", "lyft.com", "shopify.com",
    "yahoo.com", "duckduckgo.com", "whatsapp.com", "telegram.org", "signal.org",
    "slack.com", "discord.com", "canva.com", "figma.com", "notion.so",
    "gitlab.com", "bitbucket.org", "cloudflare.net", "fastly.com", "akamai.com",
    "salesforce.com", "oracle.com", "ibm.com", "intel.com", "cisco.com"
]

def build_dns_query_wire(domain: str, qtype: int = 1) -> bytes:
    """Builds RFC 1035 wireformat DNS query."""
    tx_id = random.randint(1000, 65535)
    header = tx_id.to_bytes(2, "big") + b"\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00"
    qname = b""
    for part in domain.split("."):
        b_part = part.encode("ascii")
        qname += len(b_part).to_bytes(1, "big") + b_part
    qname += b"\x00"
    qtype_class = qtype.to_bytes(2, "big") + b"\x00\x01"
    return header + qname + qtype_class


def save_packets_to_pcap(
    raw_events: List[Tuple[str, float, bytes]],
    client_ip: str,
    client_port: int,
    remote_ip: str,
    remote_port: int,
    proto: str,
    output_pcap: str
) -> int:
    """
    Converts recorded raw events [(direction, timestamp, payload), ...]
    into standard Ethernet/IP/TCP or UDP packets and writes to PCAP.
    """
    packets = []
    seq_up = 1000
    ack_up = 2000

    for direction, ts, payload in raw_events:
        if direction == "upstream":
            src_ip, dst_ip = client_ip, remote_ip
            src_port, dst_port = client_port, remote_port
        else:
            src_ip, dst_ip = remote_ip, client_ip
            src_port, dst_port = remote_port, client_port

        if proto.upper() == "TCP":
            ip_layer = IP(src=src_ip, dst=dst_ip)
            if direction == "upstream":
                tcp_layer = TCP(sport=src_port, dport=dst_port, flags="PA", seq=seq_up, ack=ack_up)
                seq_up += max(1, len(payload))
            else:
                tcp_layer = TCP(sport=src_port, dport=dst_port, flags="PA", seq=ack_up, ack=seq_up)
                ack_up += max(1, len(payload))
            pkt = ip_layer / tcp_layer / payload
        else:
            ip_layer = IP(src=src_ip, dst=dst_ip)
            udp_layer = UDP(sport=src_port, dport=dst_port)
            pkt = ip_layer / udp_layer / payload

        pkt.time = float(ts)
        packets.append(pkt)

    Path(output_pcap).parent.mkdir(parents=True, exist_ok=True)
    scapy.wrpcap(output_pcap, packets)
    return len(packets)

