import sys
import socket
import DES
import datetime
import numpy as np

port = 8888

if __name__ == "__main__":
    KDC_ip = '127.0.0.1'
    print(sys.argv)
    if len(sys.argv) >= 2:
        KDC_ip = sys.argv[1]

    u = b"BOB"
    key = 192
    key10 = np.concatenate((DES.byte_to_arr(key), np.zeros(2)))
    
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    s.connect((KDC_ip, port))
    
    s.sendall(u)
    R = s.recv(1024)
    R = R.decode("utf-8")
    
    if R == "200 OK":
        print("Everyone connected to KDC.")
    else:
        raise RuntimeError("ERROR - Not everyone connected to KDC.")

    # s.close()
    # waiting patiently for packet with symmetric key
    print("waiting.")
    new_s = socket.socket()
    new_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    new_s.bind(('', 3333))
    new_s.listen(1)
    conn, addr = new_s.accept()
    R = conn.recv(1024).decode('utf-8')
    L = R.split(',')
    session_key = int(DES.full_decrypt(L[0], key10))
    print(session_key)
    user_id = DES.full_decrypt(L[1], key10)
    T = DES.full_decrypt(L[2], key10)
    D = datetime.datetime.strptime(T, '%Y-%m-%d %H:%M:%S')
    diff = datetime.datetime.now() - D
    assert diff < datetime.timedelta(0, 5, 0) # timeout of 5 seconds to prevent replay attacks.
    
    print("sending message")
    message = "Meet me at the park at 7 PM."
    message_enc = DES.full_encrypt(message, np.concatenate((DES.byte_to_arr(session_key), np.zeros(2))))
    conn.sendall(str.encode(message_enc))
    s.close()
