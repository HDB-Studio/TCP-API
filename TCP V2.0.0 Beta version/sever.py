import socket
import threading

class ServerApp:
    def __init__(self, host='0.0.0.0', port=11111):
        self.host = host
        self.port = port
        self.server_socket = None

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"服务器启动，监听 {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"新连接来自 {client_address}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        try:
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                print(f"收到消息: {message}")
                response = f"服务器已收到: {message}"
                client_socket.send(response.encode('utf-8'))
        except Exception as e:
            print(f"处理客户端时出错: {str(e)}")
        finally:
            client_socket.close()
            print("客户端连接已关闭")

if __name__ == "__main__":
    server = ServerApp()
    server.start()
