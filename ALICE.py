import sys
import socket
import DES
import time
import numpy as np
import datetime

port = 8888

if __name__ == "__main__":
    KDC_ip = '127.0.0.1'
    print(sys.argv)
    if len(sys.argv) >= 2:
        KDC_ip = sys.argv[1]

    u = b"ALICE"
    key = 100
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
    
    print("sending request to KDC.")
    s.sendall(b"ALICE")
    request = "BOB,100"
    request_enc = str.encode(DES.full_encrypt(request, key10))
    s.sendall(request_enc)
    
    
    R = s.recv(1024)
    R = R.decode("utf-8")
    L = R.split(',')
    session_key = int(DES.full_decrypt(L[0], key10))
    bob_ip = DES.full_decrypt(L[1], key10).split("'")[1].split("'")[0]
    print(bob_ip)
    N = int(DES.full_decrypt(L[2], key10))
    assert N == 100 # authentication of N
    T = DES.full_decrypt(L[3], key10)

    # check timestamp issues
    D = datetime.datetime.strptime(T, '%Y-%m-%d %H:%M:%S')
    diff = datetime.datetime.now() - D
    assert diff < datetime.timedelta(0, 5, 0) # have a timeout of 5 seconds to prevent replay attacks
    # send rest of package to BOB:
    package = str.encode(L[4] + "," + L[5] + "," + L[6])
    
    news = socket.socket()
    news.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    news.connect((bob_ip, 3333))
    news.sendall(package)

    R = news.recv(1024).decode("utf-8")
    print(session_key)
    R_dec = DES.full_decrypt(R, np.concatenate((DES.byte_to_arr(session_key), np.zeros(2))))
    print(R_dec)
    s.close()
