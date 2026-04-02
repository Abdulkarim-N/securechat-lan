from network import start_host, start_client
from handshake import perform_handshake
from messaging import start_chat

DEFAULT_PORT = 5000

def establish_connection():
    user = input("Input 1 to host, 2 to connect: ")
    if user == "1":
        connection = start_host(DEFAULT_PORT)
        mode = "host"
    elif user == "2":
        connected_ip = input("What IP do you want to connect to? ")
        connection = start_client(connected_ip, DEFAULT_PORT)
        mode = "client"
    else:
        print("Invalid option, please input 1 or 2")
        return establish_connection()
    return connection, mode

if __name__ == '__main__':
    connection, mode = establish_connection()
    aes_key = perform_handshake(connection, mode)
    start_chat(connection, aes_key)