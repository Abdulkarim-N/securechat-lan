import os
from utils import send_msg, recv_msg
from crypto import encrypt, decrypt

# Message type prefixes
MSG_FILE_HEADER = b"F"
MSG_FILE_CHUNK = b"C"
MSG_FILE_END = b"E"

CHUNK_SIZE = 4096  # 4KB per chunk

def send_file(sock, aes_key, filepath):
    if not os.path.exists(filepath):
        print("File not found")
        return
    
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    chunk_count = (filesize + CHUNK_SIZE - 1) // CHUNK_SIZE
    
    # Step 1 - send header
    header = f"{filename}|{chunk_count}".encode()
    send_msg(sock, encrypt(aes_key, MSG_FILE_HEADER + header))
    print(f"Sending {filename} ({filesize} bytes) in {chunk_count} chunks...")
    
    # Step 2 - send chunks
    with open(filepath, "rb") as f:
        chunk_number = 0
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            encrypted_chunk = encrypt(aes_key, chunk)
            chunk_number_bytes = chunk_number.to_bytes(4, byteorder="big")
            send_msg(sock, encrypt(aes_key, MSG_FILE_CHUNK + chunk_number_bytes + encrypted_chunk))
            chunk_number += 1
            print(f"Sent chunk {chunk_number}/{chunk_count}")
    
    # Step 3 - send end signal
    send_msg(sock, encrypt(aes_key, MSG_FILE_END + filename.encode()))
    print(f"File {filename} sent successfully")

def receive_file(sock, aes_key, header_data):
    # parse header — format: filename|chunk_count
    header = header_data.decode()
    filename, chunk_count = header.split("|")
    chunk_count = int(chunk_count)
    
    print(f"\nIncoming file: {filename} ({chunk_count} chunks)")
    
    chunks = {}
    
    # Step 1 - receive all chunks
    while len(chunks) < chunk_count:
        raw = recv_msg(sock)
        data = decrypt(aes_key, raw)
        msg_type = data[:1]
        
        if msg_type == MSG_FILE_CHUNK:
            chunk_number = int.from_bytes(data[1:5], byteorder="big")
            encrypted_chunk = data[5:]
            decrypted_chunk = decrypt(aes_key, encrypted_chunk)
            chunks[chunk_number] = decrypted_chunk
            print(f"Received chunk {chunk_number + 1}/{chunk_count}")
        
        elif msg_type == MSG_FILE_END:
            break
    
    # Step 2 - reassemble in correct order
    output_filename = f"received_{filename}"
    with open(output_filename, "wb") as f:
        for i in range(chunk_count):
            if i in chunks:
                f.write(chunks[i])
            else:
                print(f"Warning: missing chunk {i}")
    
    print(f"File saved as {output_filename}")