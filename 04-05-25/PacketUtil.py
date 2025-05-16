import struct
import ast

HEADER_FORMAT = '>IIB'  # packet_type (4), payload_length (4), checksum (1)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
INFO_MESSAGE = 1
ACTION_MESSAGE = 2
CHAT_MESSAGE = 3
GAME_LOG_MESSAGE = 4
RESPONSE_MESSAGE = 5

class PacketUtil:
    
    def get_checksum(self, payload_bytes: bytes) -> int:
        return sum(payload_bytes) % 256 #sum-based

    def create_packet(self, packet_type: int, payload: str) -> bytes:
        payload_bytes = payload.encode('utf-8')
        payload_length = len(payload_bytes)
        checksum = self.get_checksum(payload_bytes)
        header = struct.pack(HEADER_FORMAT, packet_type, payload_length, checksum)
        return header + payload_bytes

    def recv_exact(self,sock, num_bytes: int) -> bytes:
        data = b''
        while len(data) < num_bytes:
            chunk = sock.recv(num_bytes - len(data))
            if not chunk:
                raise ConnectionError("Socket closed")
            data += chunk
        return data

    def receive_message(self,sock):
        header_data = self.recv_exact(sock, HEADER_SIZE)
        packet_type, payload_len, checksum = struct.unpack(HEADER_FORMAT, header_data)
        
        payload_data = self.recv_exact(sock, payload_len)
        
        # Verify checksum
        if self.get_checksum(payload_data) != checksum:
            raise ValueError("Checksum mismatch! Packet corrupted.")

        return_message = ast.literal_eval(payload_data.decode('utf-8'))

        if packet_type == INFO_MESSAGE:
            if return_message["message_type"] != "INFO":
                raise ValueError(f"Packet type vs Message mismatch! Packet Type: INFO Message Type: {return_message['message_type']} received.")

        elif packet_type == ACTION_MESSAGE:
            if return_message["message_type"] != "ACTION":
                raise ValueError(f"Packet type vs Message mismatch! Packet Type: ACTION Message Type: {return_message['message_type']} received.")

        elif packet_type == CHAT_MESSAGE:
            if return_message["message_type"] != "CHAT":
                raise ValueError(f"Packet type vs Message mismatch! Packet Type: CHAT Message Type: {return_message['message_type']} received.")

        elif packet_type == GAME_LOG_MESSAGE:
            if return_message["message_type"] != "GAME_LOG":
                raise ValueError(f"Packet type vs Message mismatch! Packet Type: GAME_LOG Message Type: {return_message['message_type']} received.")

        elif packet_type == RESPONSE_MESSAGE:
            if return_message["message_type"] != "RESPONSE":
                raise ValueError(f"Packet type vs Message mismatch! Packet Type: RESPONSE Message Type: {return_message['message_type']} received.")




        return return_message