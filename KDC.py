import DES
import connection
import numpy as np
import socket
import select
import multiprocessing



port = 8888

# connects without a blocking call to the main thread
# we can do both at the same time...
def do_connect(s, port, conn_dict):
    s.listen(1)
    conn, addr = s.accept()
    ID = conn.recv(1024)
    conn_dict[ID] = (addr, conn)

if __name__ == "__main__":

    # SETUP PHASE, MAKE SURE THAT ALICE AND BOB ARE CONNECTED TO KDC.
    # assuming private keys with KDC already set...
    Alice = connection.Connection(100, "ALICE")
    Bob = connection.Connection(192, "BOB")
    
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', port))
    
    # wait for connections with two users.
    manager = multiprocessing.Manager()
    
    conn_dict = manager.dict()

    p1 = multiprocessing.Process(target=do_connect,
                                 args=(s, port, conn_dict))
    p2 = multiprocessing.Process(target=do_connect,
                                 args=(s, port, conn_dict))
    p1.start()
    p2.start()

    p1.join()
    p2.join()
    print(conn_dict)

    fds = []
    
    # should have both Alice and Bob connected!!! send 200 OK to start symmetric key distribution.
    for conn in conn_dict.values():
        conn[1].sendall(b"200 OK")
        fds.append(conn[1])

    # wait patiently for a request to make a symmetric session key.
    readable, writable, exceptional = select.select(fds, [], [])
    for C in readable:
        ID = C.recv(1024)
        ID = ID.decode("utf-8")[:-1]
        # ID user is going to request a session key!
        # beyond the ID, everything is going to be encrypted with
        # KDC and user's personal key.

        request_enc = C.recv(1024).decode("utf-8")
        print(connection.KEYS[ID])
        key10 = np.concatenate((DES.byte_to_arr(connection.KEYS[ID]), np.zeros(2)))
        print(key10)
        request = DES.full_encrypt(request_enc, key10)
        print(request)
