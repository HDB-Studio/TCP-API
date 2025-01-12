import socket

def main():
    host = ip  # 例如 '192.168.1.100'
    port = 11111

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    while True:
        message = txt
        client_socket.send(message.encode('utf-8'))
        response = client_socket.recv(102400).decode('utf-8')
        print(f"{response}")

if __name__ == "__main__":
    main()
