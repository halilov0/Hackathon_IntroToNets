import socket
import threading
import time
import struct
import os

from NetworkUtils import (
    BROADCAST_IP, BROADCAST_PORT,
    SERVER_LISTEN_UDP_PORT, SERVER_LISTEN_TCP_PORT,
    create_broadcast_socket, create_udp_server_socket, create_tcp_server_socket
)
from PacketHandler import (
    build_offer_packet, parse_request_packet, build_payload_packet
)

class MyServer:
    def __init__(self):
        # Create sockets
        self.broadcast_socket = create_broadcast_socket()
        self.udp_server_socket = create_udp_server_socket(SERVER_LISTEN_UDP_PORT)
        self.tcp_server_socket = create_tcp_server_socket(SERVER_LISTEN_TCP_PORT)
        self.is_running = True

    def start(self):
        print("Server started. Broadcasting offers and listening for requests...")
        # Start broadcast thread
        threading.Thread(target=self._broadcast_offers, daemon=True).start()
        # Start thread to handle UDP requests
        threading.Thread(target=self._handle_udp_requests, daemon=True).start()
        # Start thread to handle the TCP accept loop if needed
        # But in the assignment, clients connect on their own after seeing the offer
        # so we only accept them on demand in a new thread for each request. 
        # We will keep listening anyway for clarity
        threading.Thread(target=self._tcp_accept_loop, daemon=True).start()

    def stop(self):
        self.is_running = False
        self.broadcast_socket.close()
        self.udp_server_socket.close()
        self.tcp_server_socket.close()

    def _broadcast_offers(self):
        """
        Sends an offer message every 1 second on broadcast.
        """
        while self.is_running:
            offer_packet = build_offer_packet(SERVER_LISTEN_UDP_PORT, SERVER_LISTEN_TCP_PORT)
            self.broadcast_socket.sendto(offer_packet, ("<broadcast>", BROADCAST_PORT))
            time.sleep(1)

    def _handle_udp_requests(self):
        """
        Wait for request packets on the UDP server socket.
        For each valid request, spawn a thread to handle the 'speed test' (TCP+UDP).
        """
        
        while self.is_running:
            try:
                data, addr = self.udp_server_socket.recvfrom(1024)
                file_size = parse_request_packet(data)
                if file_size is not None:
                    print(f"[Server] Received UDP request for {file_size} bytes from {addr}")
                    # Spin up a thread for this new 'transfer' request
                    threading.Thread(target=self._serve_client, args=(addr, file_size), daemon=True).start()
                else:
                    print(f"[Server] Invalid request from {addr}")
            except Exception as e:
                if not self.is_running:
                    break
                
    def _tcp_accept_loop(self):
        """
        Continuously accept TCP connections. Typically, we match them to a request by IP/port.
        But for simplicity, we accept and serve them in a thread.
        """
        while self.is_running:
            try:
                conn, addr = self.tcp_server_socket.accept()
                print(f"[Server] Accepted TCP connection from {addr}")
                # Typically, we'd identify which request this correlates to.
                # For demo, we store it or handle it directly if we want.
                # We'll just keep the socket in a dictionary keyed by the address, or handle immediately.
                # But let's do a simple handle:
                threading.Thread(target=self._handle_tcp_connection, args=(conn, addr), daemon=True).start()
            except:
                if not self.is_running:
                    break

    def _handle_tcp_connection(self, conn, addr):
        """
        After a client connects on TCP, we read the file size from them (simple approach).
        Then respond with that many bytes, for example.
        In the assignment, you might have them send the file size as a string plus newline.
        """
        try:
            data = conn.recv(64)  # read file size line
            if not data:
                conn.close()
                return
            try:
                file_size = int(data.decode().strip())
            except:
                print(f"[Server] Error parsing file size from {addr}")
                conn.close()
                return

            # Send the requested bytes
            dummy_data = os.urandom(file_size)  # random bytes
            conn.sendall(dummy_data)
            print(f"[Server] Sent {file_size} bytes via TCP to {addr}")
        except Exception as e:
            print(f"[Server] TCP error with {addr}: {e}")
        finally:
            conn.close()

    def _serve_client(self, client_addr, file_size):
        """
        Handle the actual "speed test" for this client over UDP.
        Send the requested file size in smaller segments to avoid exceeding UDP limits.
        """
        # Total segments and segment size
        total_segments = (file_size + 65000) // 65001  # Example: divide the file into 10 segments
        segment_size = 65001  # Ensure max segment size is 1472 bytes

        #self.udp_server_socket.settimeout(1)  # Set a timeout for the client

        total_sent = 0 # in bytes

        for segment in range(total_segments):
            payload_size = min(segment_size, file_size - total_sent)  # Adjust size for the last segment
            payload = os.urandom(payload_size)  # Generate random data

            # Build the packet (header + payload)
            packet = build_payload_packet(total_segments, segment + 1, payload)
            self.udp_server_socket.sendto(packet, client_addr)

            total_sent += payload_size

        print(f"[Server] Finished UDP transfer to {client_addr} with total {total_sent}")
        #self.udp_server_socket.close()


def main():
    server = MyServer()
    server.start()
    print("Press Ctrl+C to stop the server...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.stop()

if __name__ == "__main__":
    main()
