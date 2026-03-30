from network import start_host, start_client
from utils import send_msg, recv_msg

DEFAULT_PORT = 5000

def establish_connection():
    # 
    user = input("Host or connect? ") # user puts 1 or 2 (for now)
    if user == "1":
        connection = start_host(DEFAULT_PORT)
    elif user == "2":
        connected_Ip = input("what Ip do you want to connect to? ")
        connection  = start_client(connected_Ip,DEFAULT_PORT)
    else:
         print('Invalid option, please input 1 or 2')
         return establish_connection()
    return connection, user

def start_chat(connection, user): #test func mostly
    while True:
            if user == "2":
                message = input("Send a message: ")
                send_msg(connection,message.encode())
            elif user == "1":
                data = recv_msg(connection)
                print(f"Received: {data.decode()}")

if __name__ == '__main__':
    connection, user = establish_connection()
    start_chat(connection, user)




