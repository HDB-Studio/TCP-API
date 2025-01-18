import socket
import threading

# 广播端口和消息
BROADCAST_PORT = 37020
BROADCAST_MESSAGE = "DISCOVER_SERVER"
RESPONSE_MESSAGE = "SERVER_HERE"

def handle_client(client_socket, addr):
    client_ip = addr[0]  # 获取客户端的IP地址
    print(f"接受到连接，IP地址：{client_ip}")
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"来自{client_ip}的消息：{message}")
                client_socket.send(f"服务器已收到消息".encode('utf-8'))
            else:
                break
        except ConnectionResetError:
            break
    client_socket.close()
    print(f"连接{client_ip}已关闭")

def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # 连接到一个外部服务器，这里使用Google的DNS服务器
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return "无法获取IP地址"

def udp_broadcast_response():
    """响应UDP广播请求"""
    udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_server.bind(('', BROADCAST_PORT))
    print(f"UDP broadcast listening on port {BROADCAST_PORT}")

    while True:
        message, addr = udp_server.recvfrom(1024)
        if message.decode() == BROADCAST_MESSAGE:
            print(f"Broadcast discovery received from {addr}, responding...")
            udp_server.sendto(RESPONSE_MESSAGE.encode(), addr)

def main():
    host = '0.0.0.0'  # 监听所有可用接口
    port = 11111

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    local_ip = get_local_ip()
    print(f"服务器启动，监听端口{port}，本机IP地址：{local_ip}")

    # 启动UDP广播响应线程
    udp_thread = threading.Thread(target=udp_broadcast_response)
    udp_thread.daemon = True
    udp_thread.start()

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

if __name__ == "__main__":
    main()