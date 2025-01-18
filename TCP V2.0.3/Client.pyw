import requests
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import socket
from datetime import datetime
import sys
import webbrowser

# 获取最新版本号的 URL
VERSION_URL = 'http://47.115.75.234/tcp'
UPDATE_URL = 'https://github.com/HDB-Studio/TCP-API/tree/main/TCP%20V2.1.0'  # 替换为您的 GitHub 仓库地址
CURRENT_VERSION = "2.0.3"  # 这里定义当前版本号

# 获取当前版本
cv=" (預發布版)"

# 自动更新相关函数
def get_latest_version():
    """访问http://47.115.75.234/tcp获取最新版本号"""
    response = requests.get(VERSION_URL)
    if response.status_code == 200:
        return response.text.strip()
    else:
        raise Exception('获取最新版本信息失败。')

def check_version_and_prompt_update(gui):
    """检查版本并提示更新"""
    try:
        latest_version = get_latest_version()
        if CURRENT_VERSION < latest_version:
            gui.log(f"目前版本: {CURRENT_VERSION}")
            gui.log(f"最新版本: {latest_version}")
            gui.log("有新版本可用。")
            
            if messagebox.askyesno("有更新可用", f"有新的版本({latest_version})，要更新吗？"):
                webbrowser.open(UPDATE_URL)
                sys.exit(0)  # 退出程序以便更新
        else:
            gui.log("当前版本已是最新。")
    except Exception as e:
        gui.log(f"检查更新时出错: {e}")

def show_about():
    about_window = tk.Toplevel()
    about_window.title("关于")

    developers_label = tk.Label(about_window, text="开发者: ㄑ§ㄖ, Mixest, GPT 4o")
    developers_label.pack(padx=10, pady=5)
    
    latest_version = get_latest_version()
    if CURRENT_VERSION > latest_version:
        current_version_label = tk.Label(about_window, text=f"目前版本: {CURRENT_VERSION}{cv}")
        current_version_label.pack(padx=10, pady=5)
    else:
        current_version_label = tk.Label(about_window, text=f"目前版本: {CURRENT_VERSION}")
        current_version_label.pack(padx=10, pady=5)
    latest_version = get_latest_version()

    latest_version_label = tk.Label(about_window, text=f"最新版本: {latest_version}")
    latest_version_label.pack(padx=10, pady=5)

    website_label = tk.Label(about_window, text="官网: http://47.115.75.234/tcpapi", fg="blue", cursor="hand2")
    website_label.pack(padx=10, pady=5)
    website_label.bind("<Button-1>", lambda e: webbrowser.open_new("http://47.115.75.234/tcpapi"))

    version_service_label = tk.Label(about_window, text="版本服务网址: http://47.115.75.234/tcp", fg="blue", cursor="hand2")
    version_service_label.pack(padx=10, pady=5)
    version_service_label.bind("<Button-1>", lambda e: webbrowser.open_new("http://47.115.75.234/tcp"))
    
    website_label = tk.Label(about_window, text="Github: https://github.com/HDB-Studio/TCP-API", fg="blue", cursor="hand2")
    website_label.pack(padx=10, pady=5)
    website_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/HDB-Studio/TCP-API"))

    developers_label = tk.Label(about_window, text="HDB Studio (C) TCP-API")
    developers_label.pack(padx=10, pady=5)

# GUI 应用程序相关函数
BROADCAST_PORT = 37020
BROADCAST_MESSAGE = "DISCOVER_SERVER"

# 广播搜索服务器
def discover_servers(gui):
    gui.log(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - 搜索服务器中...')
    gui.scroll_to_bottom()
    
    # 使用 UDP 广播来发现局域网内的服务器
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(5)
        s.sendto(BROADCAST_MESSAGE.encode(), ('<broadcast>', BROADCAST_PORT))
        
        while True:
            try:
                data, addr = s.recvfrom(1024)
                gui.log(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - 发现服务器: {addr[0]}')
                gui.scroll_to_bottom()
                gui.server_listbox.insert(tk.END, addr[0])
            except socket.timeout:
                break

# 原始的 TCP 客户端代码
def tcp_client(gui, host, port, message):
    try:
        if gui.socket is None:
            gui.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            gui.socket.connect((host, port))
            gui.log(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - 已连接到 {host}:{port}')
        
        gui.socket.sendall(message.encode())
        data = gui.socket.recv(1024)
        gui.log(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {data.decode()}')
    except Exception as e:
        gui.log(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - 错误: {str(e)}')
        if gui.socket:
            gui.socket.close()
            gui.socket = None
    finally:
        gui.scroll_to_bottom()

# GUI 应用程序
class TCPClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TCP 客户端")
        
        self.host_label = ttk.Label(root, text="主机:")
        self.host_label.grid(column=0, row=0, padx=5, pady=5)
        
        self.host_entry = ttk.Entry(root)
        self.host_entry.grid(column=1, row=0, padx=5, pady=5)
        
        self.port_label = ttk.Label(root, text="端口:")
        self.port_label.grid(column=0, row=1, padx=5, pady=5)
        
        self.port_entry = ttk.Entry(root)
        self.port_entry.grid(column=1, row=1, padx=5, pady=5)
        
        # 搜索服务器按钮
        self.search_button = ttk.Button(root, text="搜索服务器", command=self.search_servers)
        self.search_button.grid(column=0, row=2, columnspan=2, padx=5, pady=5)
        
        # 服务器列表框
        self.server_listbox = tk.Listbox(root)
        self.server_listbox.grid(column=0, row=3, columnspan=2, padx=5, pady=5)
        self.server_listbox.bind('<<ListboxSelect>>', self.on_server_select)
        
        # 创建一个独立的框架用于消息输入和发送按钮
        self.message_frame = ttk.LabelFrame(root, text="消息")
        self.message_frame.grid(column=0, row=4, columnspan=2, padx=5, pady=5, sticky="ew")
        
        self.message_entry = ttk.Entry(self.message_frame)
        self.message_entry.grid(column=0, row=0, padx=5, pady=5)
        self.message_entry.bind('<Return>', self.send_message)
        
        self.send_button = ttk.Button(self.message_frame, text="发送", command=self.send_message)
        self.send_button.grid(column=1, row=0, padx=5, pady=5)
        
        self.output_text = tk.Text(root, height=10, width=50)
        self.output_text.grid(column=0, row=5, columnspan=2, padx=5, pady=5)
        
        self.socket = None  # 初始化 socket 属性
        
        # 添加检查更新按钮
        self.update_button = ttk.Button(root, text="检查更新", command=lambda: check_version_and_prompt_update(self))
        self.update_button.grid(column=0, row=6, columnspan=2, padx=5, pady=5)
        
        # 添加关于按钮
        self.about_button = ttk.Button(root, text="关于", command=show_about)
        self.about_button.grid(column=0, row=7, columnspan=2, padx=5, pady=5)
        
        # 添加关闭连接按钮
        self.close_button = ttk.Button(root, text="关闭连接", command=self.close_connection)
        self.close_button.grid(column=0, row=8, columnspan=2, padx=5, pady=5)

    def search_servers(self):
        threading.Thread(target=discover_servers, args=(self,)).start()

    def on_server_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self.host_entry.delete(0, tk.END)
            self.host_entry.insert(0, event.widget.get(index))

    def send_message(self, event=None):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        message = self.message_entry.get()
        # 发送完信息后清空信息栏并锁定
        self.message_entry.delete(0, tk.END)
        self.message_entry.config(state=tk.DISABLED)
        # 使用多线程来避免阻塞主界面
        threading.Thread(target=self.threaded_send, args=(host, port, message)).start()

    def threaded_send(self, host, port, message):
        tcp_client(self, host, port, message)
        # 完成发送后解锁信息栏
        self.root.after(0, self.unlock_message_entry)
        
    def unlock_message_entry(self):
        self.message_entry.config(state=tk.NORMAL)
        self.message_entry.focus()

    def close_connection(self):
        """关闭当前的 TCP 连接"""
        if self.socket:
            self.socket.close()
            self.socket = None
            self.log("连接已关闭。")

    def scroll_to_bottom(self):
        self.output_text.see(tk.END)

    def log(self, message):
        """在日志框中打印消息"""
        self.output_text.insert(tk.END, f"{message}\n")
        self.scroll_to_bottom()

if __name__ == "__main__":
    try:
        # 启动GUI应用程序
        root = tk.Tk()
        app = TCPClientGUI(root)
        # 检查更新
        threading.Thread(target=check_version_and_prompt_update, args=(app,)).start()
        root.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")  # 等待用户输入以防止窗口关闭
