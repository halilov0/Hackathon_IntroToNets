import socket

class NetworkUtils:
    @staticmethod
    def create_udp_socket():
        """Creates a UDP socket."""
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return udp_socket

    @staticmethod
    def create_tcp_socket():
        """Creates a TCP socket."""
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return tcp_socket

    @staticmethod
    def bind_socket(sock, port):
        """Binds a socket to a port."""
        sock.bind(('', port))

    @staticmethod
    def close_socket(sock):
        """Closes a socket."""
        try:
            sock.close()
        except Exception as e:
            print(f"Error closing socket: {e}")

    @staticmethod
    def send_udp_message(sock, message, address):
        """Sends a UDP message to the specified address."""
        sock.sendto(message, address)

    @staticmethod
    def receive_udp_message(sock, buffer_size=1024):
        """Receives a UDP message."""
        return sock.recvfrom(buffer_size)

    @staticmethod
    def send_tcp_message(sock, message):
        """Sends a TCP message."""
        sock.sendall(message)

    @staticmethod
    def receive_tcp_message(sock, buffer_size=1024):
        """Receives a TCP message."""
        return sock.recv(buffer_size)
