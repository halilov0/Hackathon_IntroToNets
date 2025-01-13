import struct
from NetworkUtils import MAGIC_COOKIE, MSG_TYPE_OFFER, MSG_TYPE_REQUEST, MSG_TYPE_PAYLOAD

"""
Packet Formats (all multi-byte fields in network byte order):

OFFER message (server -> client):
  magic cookie (4 bytes) = 0xabcdcdba
  msg_type (1 byte)      = 0x2
  server_udp_port (2 bytes)
  server_tcp_port (2 bytes)

REQUEST message (client -> server):
  magic cookie (4 bytes) = 0xabcdcdba
  msg_type (1 byte)      = 0x3
  file_size (8 bytes)    = <requested bytes>

PAYLOAD message (server -> client):
  magic cookie (4 bytes) = 0xabcdcdba
  msg_type (1 byte)      = 0x4
  total_segments (8 bytes)
  current_segment (8 bytes)
  payload (variable length)
"""

def build_offer_packet(udp_port, tcp_port):
    """
    Returns a bytes object containing the offer packet.
    """
    return struct.pack(
        "!IbHHi",   # ! -> network byte order, I=4 bytes, b=1 byte, H=2 bytes, H=2 bytes, i=4 bytes (We can’t do 2+2=4 directly for the ports if we want them as H)
        MAGIC_COOKIE,
        MSG_TYPE_OFFER,
        udp_port,
        tcp_port,
        0  # sometimes you might want to place placeholder or reduce the format
    )[:9]  # trim to only the first 9 bytes if you don't want the extra 4 from 'i'

def parse_offer_packet(data):
    """
    Returns (udp_port, tcp_port) if valid, else None.
    We expect 9 bytes: 4 (cookie) + 1 (type) + 2 (udp) + 2 (tcp).
    """
    if len(data) < 9:
        return None
    unpacked = struct.unpack("!IbHH", data[:9])
    cookie, msg_type, udp_port, tcp_port = unpacked
    if cookie == MAGIC_COOKIE and msg_type == MSG_TYPE_OFFER:
        return udp_port, tcp_port
    return None

def build_request_packet(file_size):
    """
    Returns a bytes object for request: 4 + 1 + 8 = 13 bytes.
    """
    return struct.pack(
        "!IbQ",   # I=4 bytes, b=1 byte, Q=8 bytes
        MAGIC_COOKIE,
        MSG_TYPE_REQUEST,
        file_size
    )

def parse_request_packet(data):
    """
    Returns file_size if valid, else None.
    Expect 13 bytes.
    """
    if len(data) < 13:
        return None
    unpacked = struct.unpack("!IbQ", data[:13])
    cookie, msg_type, file_size = unpacked
    if cookie == MAGIC_COOKIE and msg_type == MSG_TYPE_REQUEST:
        return file_size
    return None

def build_payload_packet(total_segments, current_segment, payload):
    """
    Payload message: 4 + 1 + 8 + 8 + len(payload).
    We'll pack the header first, then append the payload.
    """
    header = struct.pack("!IbQQ", MAGIC_COOKIE, MSG_TYPE_PAYLOAD, total_segments, current_segment)
    return header + payload

def parse_payload_packet(data):
    """
    Returns (total_segments, current_segment, payload_data) if valid.
    Expect at least 4+1+8+8 = 21 bytes for the header.
    """
    if len(data) < 21:
        return None
    header = data[:21]
    unpacked = struct.unpack("!IbQQ", header)
    cookie, msg_type, total_segments, current_segment = unpacked
    if cookie == MAGIC_COOKIE and msg_type == MSG_TYPE_PAYLOAD:
        payload_data = data[21:]
        return total_segments, current_segment, payload_data
    return None
