
import socket
import subprocess
import re
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import ipaddress

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("多功能网络客户端")
        self.root.geometry("500x600")

        self.create_widgets()
        self.client_socket = None
        self.connected_ip = None

    def create_widgets(self):
        # Wi-Fi 信息
        ttk.Label(self.root, text="当前连接的Wi-Fi:").pack(pady=5)
        self.wifi_label = ttk.Label(self.root, text="")
        self.wifi_label.pack()
        self.update_wifi_info()

        # 网络信息
        ttk.Label(self.root, text="当前网络信息:").pack(pady=5)
        self.network_label = ttk.Label(self.root, text="")
        self.network_label.pack()
        self.update_network_info()

        # 服务器搜索
        ttk.Label(self.root, text="局域网内可用服务器:").pack(pady=5)
        self.server_listbox = tk.Listbox(self.root, height=5)
        self.server_listbox.pack(fill=tk.BOTH, expand=True, padx=10)
        ttk.Button(self.root, text="搜索服务器", command=self.search_servers).pack(pady=5)

        # 连接按钮
        ttk.Button(self.root, text="连接到选中的服务器", command=self.connect_to_server).pack(pady=5)

        # 消息发送
        self.message_entry = ttk.Entry(self.root, width=50)
        self.message_entry.pack(pady=5)
        ttk.Button(self.root, text="发送消息", command=self.send_message).pack()

        # 消息显示
        self.message_text = tk.Text(self.root, height=10, width=50)
        self.message_text.pack(pady=10)

        # 错误信息显示
        self.error_label = ttk.Label(self.root, text="", foreground="red")
        self.error_label.pack(pady=5)

    def update_wifi_info(self):
        wifi_name = self.get_wifi_name()
        self.wifi_label.config(text=wifi_name if wifi_name else "未连接到Wi-Fi")

    def get_wifi_name(self):
        try:
            if subprocess.call("netsh wlan show interfaces") == 0:
                wifi_info = subprocess.check_output("netsh wlan show interfaces").decode('utf-8', errors='ignore')
                ssid = re.search(r"SSID\s+:\s(.+)", wifi_info)
                return ssid.group(1) if ssid else "未知"
            else:
                return "无法获取Wi-Fi信息"
        except Exception as e:
            self.show_error(f"获取Wi-Fi信息时出错: {str(e)}")
            return "未知"

    def update_network_info(self):
        try:
            output = subprocess.check_output("ipconfig").decode('gbk', errors='ignore')
            ip_address = re.search(r"IPv4 地址[ .]+: ([^\r\n]+)", output)
            subnet_mask = re.search(r"子网掩码[ .]+: ([^\r\n]+)", output)
            if ip_address and subnet_mask:
                network = ipaddress.IPv4Network(f"{ip_address.group(1)}/{subnet_mask.group(1)}", strict=False)
                self.network_label.config(text=f"IP: {ip_address.group(1)}, 网络: {network.network_address}/{network.prefixlen}")
                self.connected_ip = ip_address.group(1)
            else:
                self.network_label.config(text="无法获取网络信息")
        except Exception as e:
            self.show_error(f"获取网络信息时出错: {str(e)}")
            self.network_label.config(text="获取网络信息失败")

    def search_servers(self):
        self.server_listbox.delete(0, tk.END)
        if not self.connected_ip:
            self.show_error("未连接到网络，无法搜索服务器")
            return
        
        network = ipaddress.IPv4Network(f"{self.connected_ip}/24", strict=False)
        for ip in network.hosts():
            threading.Thread(target=self.check_server, args=(str(ip),)).start()

    def check_server(self, ip):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                if s.connect_ex((ip, 11111)) == 0:
                    self.server_listbox.insert(tk.END, ip)
        except:
            pass

    def connect_to_server(self):
        selected = self.server_listbox.curselection()
        if not selected:
            self.show_error("请先选择一个服务器")
            return
        
        host = self.server_listbox.get(selected[0])
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, 11111))
            messagebox.showinfo("成功", f"已连接到服务器 {host}")
            self.error_label.config(text="")
        except Exception as e:
            self.show_error(f"连接服务器失败: {str(e)}")

    def send_message(self):
        if not self.client_socket:
            self.show_error("请先连接到服务器")
            return
        
        message = self.message_entry.get()
        if not message:
            self.show_error("请输入要发送的消息")
            return
        
        try:
            self.client_socket.send(message.encode('utf-8'))
            self.message_text.insert(tk.END, f"发送: {message}\n")
            self.message_entry.delete(0, tk.END)
        except Exception as e:
            self.show_error(f"发送消息失败: {str(e)}")

    def show_error(self, error_message):
        self.error_label.config(text=error_message)

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
