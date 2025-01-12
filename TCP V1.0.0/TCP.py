import socket

def main():
    host = input("服务器端电脑的局域网IP地址:")  # 例如 '192.168.1.100'
    port = 11111

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    while True:
        message = input("请输入要发送的消息：")
        client_socket.send(message.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        print(f"{response}")

if __name__ == "__main__":
    main()
