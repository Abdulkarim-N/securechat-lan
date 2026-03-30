import socket

def start_host(port):
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
    sock.connect((ip, port))

    print('You have connected!!!')

    return sock
    

def close_connection(sock):
    # simply handles a clean closure of the connection
    sock.close()

