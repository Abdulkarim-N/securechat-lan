from network import start_host, start_client

DEFAULT_PORT = 5000

print('\nwould you like to start a new connection or connect to a user directly?')
# user puts 1 or 2 (for now)

val = input('Input a 1 to start a new connection, and 2 to connect to a user:')

if val == "1":
    connection = start_host(DEFAULT_PORT)
elif val == "2":
    connected_Ip = input("what Ip do you want to connect to? ")
    connection  = start_client(connected_Ip,DEFAULT_PORT)