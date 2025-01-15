import socket

MAGIC_COOKIE = 0xabcdcdba
MSG_TYPE_OFFER   = 0x2  # Server -> Client
MSG_TYPE_REQUEST = 0x3  # Client -> Server
MSG_TYPE_PAYLOAD = 0x4  # Server -> Client payload

BROADCAST_IP = "192.168.1.80"
BROADCAST_PORT = 13117  # Example broadcast port
SERVER_LISTEN_UDP_PORT = 20250  # Example for receiving requests
SERVER_LISTEN_TCP_PORT = 20251  # Example for TCP

def create_broadcast_socket():
    """Creates a socket for broadcasting messages."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    return s

# Helper: create a UDP server socket
def create_udp_server_socket(port=SERVER_LISTEN_UDP_PORT):
    """Creates a UDP server socket."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", port))  # Listen on all interfaces
    return s

# Helper: create a TCP server socket
def create_tcp_server_socket(port=SERVER_LISTEN_TCP_PORT):
    """Creates a TCP server socket."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", port))
    s.listen(5)  # Allow up to 5 pending clients
    return s