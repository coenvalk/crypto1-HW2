import sys
import socket
import DES
import numpy as np

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
    s.sendall("ALICE")
    request = "BOB,100"
    request_enc = DES.full_encrypt(request, key10)
    s.sendall(request_enc)
    
    
    R = s.recv(1024)
    R = R.decode("utf-8")
    
