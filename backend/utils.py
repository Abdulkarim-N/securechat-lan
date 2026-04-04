import struct
# send a msg, uses the socket and data, breaks the data into byte chunks, and sends it chunk by chunk, with the header being a special character
def send_msg(sock, data):
    length = len(data)
    header = struct.pack(">I", length)
    sock.sendall(header)
    sock.sendall(data)
#recive msg is basically the same, it stats with the data being a special character, if the character is that special chunk, it stops the chat
def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if chunk == b"":
            raise ConnectionError("Connection closed unexpectedly")
        data += chunk
    return data

def recv_msg(sock):
    header = recv_exact(sock, 4)
    length = struct.unpack(">I", header)[0]
    return recv_exact(sock, length)