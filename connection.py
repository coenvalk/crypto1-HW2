import random
import datetime

KEYS = {}

class Connection:
    def __init__(self, key, u_id):
        self.key_ = key
        self.id_ = u_id

        KEYS[self.id_] = self.key_

    def get_id(self):
        return self.id_

    def get_key(self):
        return self.key_

    def add_ip(self, ip):
        self.ip_ = ip

    def setup_key_distribution(self, receiver_ID, N):
        session_key = random.getrandombits(8)
        session_key_enc_a = session_key ^ self.key_
        receiver_ID_enc_a = receiver_ID ^ self.key_
        N_enc_a = N ^ self.key_

        session_key_enc_b = session_key ^ KEYS[receiver_ID]
        sender_id_enc_b = self.id_ ^ KEYS[receiver_ID]
        timestamp = datetime.datetime.now()
        timestamp_str = unicode(timestamp)
        timestamp_str_enc_b = ""
        timestamp_str_enc_a = ""
        for char in timestamp_str:
            timestamp_str_enc_b += chr(ord(char) ^ KEYS[receiver_ID])
            timestamp_str_enc_a += chr(ord(char) ^ self.key_)

        print timestamp_str_enc_a, timestamp_str_enc_b
