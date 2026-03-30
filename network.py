import socket

def start_host(port): #start the host (TCP connection, 1 person must be 'host' and the other 'client' after that its basic p2p connection)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind(("",port))
    sock.listen()
    # print statements are for testing, remove after front end is made
    print(f"Your IP: {socket.gethostbyname(socket.gethostname())}")
    print(f"Waiting for connection on port {port}...")
    connection, address = sock.accept()
    print(f"Connected to {address[0]}!")

    # for testing for now

    return connection


def start_client(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip, port))
        print('You have connected!!!')
    except ConnectionRefusedError:
        print("Could not connect — is the host running?")
        sock.close()
        return None

    return sock
    

def close_connection(sock):
    # simply handles a clean closure of the connection
    sock.close()

