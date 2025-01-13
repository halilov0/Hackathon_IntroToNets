import struct

class PacketHandler:
    MAGIC_COOKIE = 0xabcddcba

    @staticmethod
    def encode_offer(udp_port, tcp_port):
        """Encodes an offer packet."""
        magic_cookie = PacketHandler.MAGIC_COOKIE
        message_type = 0x2
        return struct.pack('!I B H H', magic_cookie, message_type, udp_port, tcp_port)

    @staticmethod
    def decode_offer(data):
        """Decodes an offer packet."""
        try:
            magic_cookie, message_type, udp_port, tcp_port = struct.unpack('!I B H H', data)
            if magic_cookie != PacketHandler.MAGIC_COOKIE or message_type != 0x2:
                raise ValueError("Invalid offer packet.")
            return udp_port, tcp_port
        except struct.error:
            raise ValueError("Malformed packet.")

    @staticmethod
    def encode_request(file_size):
        """Encodes a request packet."""
        magic_cookie = PacketHandler.MAGIC_COOKIE
        message_type = 0x3
        return struct.pack('!I B Q', magic_cookie, message_type, file_size)

    @staticmethod
    def decode_request(data):
        """Decodes a request packet."""
        try:
            magic_cookie, message_type, file_size = struct.unpack('!I B Q', data)
            if magic_cookie != PacketHandler.MAGIC_COOKIE or message_type != 0x3:
                raise ValueError("Invalid request packet.")
            return file_size
        except struct.error:
            raise ValueError("Malformed packet.")

    @staticmethod
    def encode_payload(total_segments, current_segment, payload_data):
        """Encodes a payload packet."""
        magic_cookie = PacketHandler.MAGIC_COOKIE
        message_type = 0x4
        return struct.pack('!I B Q Q', magic_cookie, message_type, total_segments, current_segment) + payload_data

    @staticmethod
    def decode_payload(data):
        """Decodes a payload packet."""
        try:
            header_size = struct.calcsize('!I B Q Q')
            magic_cookie, message_type, total_segments, current_segment = struct.unpack(
                '!I B Q Q', data[:header_size]
            )
            if magic_cookie != PacketHandler.MAGIC_COOKIE or message_type != 0x4:
                raise ValueError("Invalid payload packet.")
            payload_data = data[header_size:]
            return total_segments, current_segment, payload_data
        except struct.error:
            raise ValueError("Malformed packet.")
