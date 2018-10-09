import connection
import numpy as np
import socket
import multiprocessing



port = 8888

# connects without a blocking call to the main thread
# we can do both at the same time...
def do_connect(s, port, ID, conn_dict, addr_dict):
    s.listen(1)
    conn, addr = s.accept()
    conn_dict[ID] = conn
    addr_dict[ID] = addr

if __name__ == "__main__":

    # SETUP PHASE, MAKE SURE THAT ALICE AND BOB ARE CONNECTED TO KDC.
    # assuming initial conection with KDC already set...
    Alice = connection.Connection(100, "ALICE")
    Bob = connection.Connection(192, "BOB")
    
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', port))
    
    # wait for connections with Alice and Bob.
    manager = multiprocessing.Manager()
    
    conn_dict = manager.dict()
    addr_dict = manager.dict()

    p1 = multiprocessing.Process(target=do_connect,
                                 args=(s, port, "ALICE", conn_dict, addr_dict))
    p2 = multiprocessing.Process(target=do_connect,
                                 args=(s, port, "BOB", conn_dict, addr_dict))
    p1.start()
    p2.start()

    p1.join()
    p2.join()

    # should have both Alice and Bob connected!!! send 200 OK to start symmetric key distribution.
    for conn in conn_dict.values():
        conn.sendall("200 OK")

    # wait patiently for a request to make a symmetric session key.
    s.
    
    
