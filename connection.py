import random
import datetime
import DES
import numpy as np

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
        sender_key_10 = np.concatenate((DES.byte_to_arr(self.key_), np.zeros(2)))
        receiver_key_10 = np.concatenate((DES.byte_to_arr(KEYS[receiver_ID]), np.zeros(2)))
        session_key = random.getrandbits(8)
        session_key_enc_a = DES.full_encrypt(str(session_key), sender_key_10)
        receiver_ID_enc_a = DES.full_encrypt(str(receiver_ID), sender_key_10)
        N_enc_a = DES.full_encrypt(str(N), sender_key_10)

        session_key_enc_b = DES.full_encrypt(str(session_key), receiver_key_10)
        sender_id_enc_b = DES.full_encrypt(str(self.id_), receiver_key_10)
        timestamp = datetime.datetime.now()
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        timestamp_str_enc_b = DES.full_encrypt(timestamp_str, receiver_key_10)
        timestamp_str_enc_a = DES.full_encrypt(timestamp_str, sender_key_10)

        return str(session_key_enc_a) + "," + str(receiver_ID_enc_a) + "," + \
            str(N_enc_a) + \
            str(timestamp_str_enc_a) + "," + str(session_key_enc_b) + "," + \
            str(sender_id_enc_b) + "," + str(timestamp_str_enc_b)
    
