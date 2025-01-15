import socket
import threading
import time
import struct

from PacketHandler import (
    parse_offer_packet, build_request_packet, parse_payload_packet
)
from NetworkUtils import (
    BROADCAST_PORT, MAGIC_COOKIE,
    MSG_TYPE_OFFER, MSG_TYPE_REQUEST, MSG_TYPE_PAYLOAD
)

class MyClient:
    number = 1
    def __init__(self):
        self.is_running = True
        self.file_size = 1024 * 1024  # default 1MB
        self.server_udp_port = None
        self.server_tcp_port = None
        self.server_ip = None

    def start(self):
        print("Client started, listening for offer requests...")
        # Thread to listen for offers
        threading.Thread(target=self._listen_for_offers, daemon=True).start()
        
        # Main loop
        while self.is_running:
            time.sleep(2)

    def _listen_for_offers(self):
        """
        Opens a UDP socket on the broadcast port and waits for server offers.
        When an offer is received, we parse it and connect automatically.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(("", BROADCAST_PORT))

        while self.is_running:
            try:
                data, addr = s.recvfrom(1024)
                offer = parse_offer_packet(data)
                if offer is not None:
                    udp_port, tcp_port = offer
                    print(f"[Client] Received offer from {addr} with ports UDP={udp_port}, TCP={tcp_port}")
                    self.server_ip = addr[0]
                    self.server_udp_port = udp_port
                    self.server_tcp_port = tcp_port
                    # Let’s do a single speed test for demo
                    threading.Thread(target=self._perform_speed_test, daemon=True).start()
            except:
                pass

    def _perform_speed_test(self):
        """
        Send a request packet to the server's UDP port, 
        then set up a TCP connection, measure speed, etc.
        """
        if not self.server_ip or not self.server_udp_port:
            return
        # Prompt or assume a file size
        # In a real assignment, we might ask the user:
        #   self.file_size = int(input("Enter file size in bytes: "))
        # For now, we keep the default self.file_size

        # Build and send the request packet
        request_data = build_request_packet(self.file_size)
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.sendto(request_data, (self.server_ip, self.server_udp_port))
        print(f"[Client] Sent request for {self.file_size} bytes to {self.server_ip}:{self.server_udp_port}")

        # Start a thread to listen for incoming UDP payload
        threading.Thread(target=self._receive_udp_data, args=(udp_sock,), daemon=True).start()

        # Now connect over TCP
        self._receive_tcp_data()

    def _receive_tcp_data(self):
        """
        Connect to the server over TCP, send the file_size as a line, 
        then read that many bytes.
        """
        if not self.server_ip or not self.server_tcp_port:
            return

        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((self.server_ip, self.server_tcp_port))
            # Send file size as a line
            conn.sendall(f"{self.file_size}\n".encode())

            start_time = time.time()
            received = 0
            data_chunks = []
            while received < self.file_size:
                chunk = conn.recv(min(4096, self.file_size - received))
                if not chunk:
                    break
                received += len(chunk)
                data_chunks.append(chunk)

            conn.close()
            end_time = time.time()
            duration = end_time - start_time
            number = MyClient.number
            speed_bits = (received * 8) / duration if duration > 0 else 0
            print(f"[Client] TCP transfer #{number} finished, total time: {duration:.2f} seconds, total speed: {speed_bits:.2f} bits/second")
            MyClient.number += 1
        except Exception as e:
            print(f"[Client][TCP] Error: {e}")

    def _receive_udp_data(self, udp_sock):
        """
        Listen for UDP payload packets and reassemble the file.
        """
        udp_sock.settimeout(1)
        total_segments = 0
        received_segments = 0
        received_data = {}
        full_payload = 0
        start_time = time.time()
        end_time = time.time()
        while True:
            try:
                packet, addr = udp_sock.recvfrom(min(65535, self.file_size - full_payload))  # Receive up to 65,535 bytes
                result = parse_payload_packet(packet)
                #print(f"should be t_segs, c_seg, payload:::: {result}")

                if result is None:
                    continue  # Skip invalid packets

                t_segs, c_seg, payload = result
                total_segments = t_segs
                received_data[c_seg] = payload 
                received_segments += 1
                full_payload += len(payload)
                end_time = time.time()

                # Break if all segments are received
                if len(received_data) == total_segments:
                    break

            except:
                duration = end_time - start_time
                speed_bits = (full_payload * 8) / duration if duration > 0 else 0
                number = MyClient.number
                percentage = (received_segments / total_segments) * 100 if total_segments > 0 else 0
                print(f"[Client] UDP transfer #{number} finished, total time: {duration:.2f} seconds, total speed: {speed_bits:.2f} bits/second, percentage of packets received successfully: {percentage:.0f}%")
                print("Timeout while waiting for packets.")
                MyClient.number += 1
                break
    
    def stop(self):
        self.is_running = False
        print("[Client] Shuttting down...")

def main():
    client = MyClient()
    try:
        client.start()
    except KeyboardInterrupt:
        print("\nStopping client...")
        client.stop()

if __name__ == "__main__":
    main()
