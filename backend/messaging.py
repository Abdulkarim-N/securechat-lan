import threading
from utils import send_msg, recv_msg
from crypto import encrypt, decrypt
from file_transfer import send_file, receive_file, MSG_FILE_HEADER

def receive_loop(sock, aes_key, stop_event):
    while not stop_event.is_set():
        try:
            data = recv_msg(sock)
            if data is None:
                print("\nPeer disconnected")
                stop_event.set()
                break
            
            message = decrypt(aes_key, data)
            msg_type = message[:1]
            content = message[1:]
            
            if msg_type == b"M":
                if content == b"/quit":
                    print("\nPeer has ended the session")
                    stop_event.set()
                    break
                print(f"\nPeer: {content.decode()}")
                print("You: ", end="", flush=True)
            
            elif msg_type == MSG_FILE_HEADER:
                receive_file(sock, aes_key, content)
                print("You: ", end="", flush=True)

        except Exception:
            if not stop_event.is_set():
                print("\nConnection lost")
            stop_event.set()
            break

def send_loop(sock, aes_key, stop_event):
    while not stop_event.is_set():
        try:
            message = input("You: ")
            
            if message.lower() == "/quit":
                encrypted = encrypt(aes_key, b"M" + b"/quit")
                send_msg(sock, encrypted)
                stop_event.set()
                break
            
            elif message.lower().startswith("/sendfile "):
                filepath = message[10:].strip()
                send_file(sock, aes_key, filepath)
            
            elif message.strip() == "":
                continue
            
            else:
                encrypted = encrypt(aes_key, b"M" + message.encode())
                send_msg(sock, encrypted)
        
        except Exception:
            stop_event.set()
            break

def start_chat(sock, aes_key):
    stop_event = threading.Event()

    recv_thread = threading.Thread(
        target=receive_loop,
        args=(sock, aes_key, stop_event),
        daemon=True
    )
    recv_thread.start()

    send_loop(sock, aes_key, stop_event)

    recv_thread.join(timeout=2)
    sock.close()
    print("\nSession ended")