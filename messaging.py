import threading
from utils import send_msg, recv_msg
from crypto import encrypt, decrypt

def receive_loop(sock, aes_key, stop_event):
    while not stop_event.is_set():
        try:
            data = recv_msg(sock)
            if data is None:
                print("\nPeer disconnected")
                stop_event.set()
                break
            message = decrypt(aes_key, data)
            if message == b"/quit":
                print("\nPeer has ended the session")
                stop_event.set()
                break
            print(f"\nPeer: {message.decode()}")
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
                encrypted = encrypt(aes_key, b"/quit")
                send_msg(sock, encrypted)
                stop_event.set()
                break
            if message.strip() == "":
                continue
            encrypted = encrypt(aes_key, message.encode())
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