from network import start_host, start_client
from utils import send_msg, recv_msg
from crypto import generate_dh_keys, serialize_public_key, deserialize_public_key

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

    private_key, public_key = generate_dh_keys()
    serialized = serialize_public_key(public_key)
    recovered = deserialize_public_key(serialized)
    print("Keys generated successfully")
    print(f"Serialized length: {len(serialized)} bytes")
    start_chat(connection, user)




