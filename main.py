from network import start_host, start_client
from utils import send_msg, recv_msg
from crypto import generate_dh_keys, serialize_public_key, deserialize_public_key, derive_session_key, derive_aes_key

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



    # Simulate both peers locally
    private_a, public_a = generate_dh_keys()
    # Simulate peer B using same parameters
    private_b = public_a.parameters().generate_private_key()
    public_b = private_b.public_key()

    # Both derive session key
    secret_a = derive_session_key(private_a, public_b)
    secret_b = derive_session_key(private_b, public_a)

    # Both derive AES key
    aes_a = derive_aes_key(secret_a)
    aes_b = derive_aes_key(secret_b)

    print(f"Keys match: {aes_a == aes_b}")  # should print True
    print(f"AES key length: {len(aes_a)} bytes")  # should print 32


    start_chat(connection, user)




