import socket
import threading
import ssl
import zlib

BROADCAST_PORT = 37020
BROADCAST_MESSAGE = "DISCOVER_SERVER"
RESPONSE_MESSAGE = "SERVER_HERE"
TCP_PORT = 11111

def highlight_message(message):
    """高亮显示消息内容"""
    return f"\033[1;31m{message}\033[0m"

def handle_client(client_socket, addr):
    client_ip = addr[0]
    print(f"接受到连接，IP地址：{client_ip}")
    while True:
        try:
            data = client_socket.recv(1024)
            if data:
                message = zlib.decompress(data).decode('utf-8')
                print(f"来自{client_ip}的消息：{highlight_message(message)}")
                response = zlib.compress("服务器已收到消息".encode('utf-8'))
                client_socket.send(response)
            else:
                break
        except (ConnectionResetError, zlib.error) as e:
            print(f"错误：{e}，来自{client_ip}的连接已断开")
            break
    client_socket.close()
    print(f"连接{client_ip}已关闭")

def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
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
    port = TCP_PORT

    use_ssl = input("是否启用SSL/TLS? (y/n): ").strip().lower() == 'y'

    if use_ssl:
        certfile = input("请输入SSL证书文件路径（例如：server.crt）：").strip()
        keyfile = input("请输入SSL密钥文件路径（例如：server.key）：").strip()
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=certfile, keyfile=keyfile)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)

    local_ip = get_local_ip()
    print(f"服务器启动，监听端口{port}，本机IP地址：{local_ip}")

    udp_thread = threading.Thread(target=udp_broadcast_response)
    udp_thread.daemon = True
    udp_thread.start()

    while True:
        client_socket, addr = server_socket.accept()
        if use_ssl:
            ssl_client_socket = context.wrap_socket(client_socket, server_side=True)
            client_thread = threading.Thread(target=handle_client, args=(ssl_client_socket, addr))
        else:
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

if __name__ == "__main__":
    main()
