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
    
    # waiting patiently for packet with symmetric key
    new_s = socket.socket()
    new_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    new_s.listen(5)
    conn, addr = new_s.accept()
    R = conn.recv(1024)
    print(R)
    
    
