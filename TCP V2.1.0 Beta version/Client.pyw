import requests, tkinter as tk, threading, socket, ssl, zlib, sys, webbrowser, os
from tkinter import filedialog, messagebox, colorchooser
from datetime import datetime
from ttkthemes import ThemedTk
import ttkbootstrap as ttkb
from PIL import Image, ImageTk

VERSION_URL = 'http://47.115.75.234/tcp'
UPDATE_URL = 'https://github.com/HDB-Studio/TCP-API/tree/main/TCP%20V2.1.1/exe/Client/Client.exe'
CURRENT_VERSION, cv = "2.1.0", " (預發布版)"
BROADCAST_PORT, BROADCAST_MESSAGE = 37020, "DISCOVER_SERVER"

def get_latest_version():
    response = requests.get(VERSION_URL)
    return response.text.strip() if response.status_code == 200 else '获取最新版本信息失败。'

def check_version_and_prompt_update():
    try:
        latest_version = get_latest_version()
        if CURRENT_VERSION < latest_version:
            messagebox.showinfo("有更新可用", f"有新的版本({latest_version})，要更新吗？")
            webbrowser.open(UPDATE_URL)
            sys.exit(0)
        else:
            messagebox.showinfo("检查更新", "当前版本已是最新。")
    except Exception as e:
        messagebox.showerror("检查更新时出错", str(e))
if CURRENT_VERSION>get_latest_version():
    a=CURRENT_VERSION+cv
else:
    a=CURRENT_VERSION
def show_about(frame):
    def update_latest_version():
        latest_version = get_latest_version()
        latest_version_label.config(text=f"最新版本: {latest_version}")
        frame.after(3000, update_latest_version)
    
    for widget in frame.winfo_children():
        widget.destroy()
    
    labels = [
        ("开发者: ㄑ§ㄖ, Mixest, GPT 4o", None),
        (f"目前版本: {a}", None)
    ]
    
    for text, url in labels:
        lbl = ttkb.Label(frame, text=text, cursor="hand2" if url else "")
        lbl.pack(padx=10, pady=5)
        if url:
            lbl.bind("<Button-1>", lambda e, url=url: webbrowser.open_new(url))
    
    latest_version_label = ttkb.Label(frame, text=f"最新版本: {get_latest_version()}")
    latest_version_label.pack(padx=10, pady=5)
    update_latest_version()
    
    additional_labels = [
        ("官网: http://47.115.75.234/tcpapi", "http://47.115.75.234/tcpapi"),
        ("版本服务网址: http://47.115.75.234/tcp", "http://47.115.75.234/tcp"),
        ("Github: https://github.com/HDB-Studio/TCP-API", "https://github.com/HDB-Studio/TCP-API"),
        ("HDB Studio (C) TCP-API", None),
    ]
    
    for text, url in additional_labels:
        lbl = ttkb.Label(frame, text=text, cursor="hand2" if url else "")
        lbl.pack(padx=10, pady=5)
        if url:
            lbl.bind("<Button-1>", lambda e, url=url: webbrowser.open_new(url))
    
    ttkb.Button(frame, text="检查更新", command=check_version_and_prompt_update, bootstyle="info").pack(padx=10, pady=5)
def show_settings(frame, settings, title):
    for widget in frame.winfo_children(): widget.destroy()
    ttkb.Label(frame, text=title, font=("Helvetica", 14)).grid(row=0, columnspan=2, padx=10, pady=5)
    for i, (text, var) in enumerate(settings):
        ttkb.Label(frame, text=text).grid(row=i+1, column=0, sticky='e', padx=10, pady=5)
        widget = ttkb.Entry(frame, textvariable=var) if isinstance(var, tk.StringVar) else ttkb.Checkbutton(frame, text=text, variable=var)
        widget.grid(row=i+1, column=1, sticky='w', padx=10, pady=5)

def discover_servers(gui):
    gui.log(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - 搜索服务器中...')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(5)
        s.sendto(BROADCAST_MESSAGE.encode(), ('<broadcast>', BROADCAST_PORT))
        while True:
            try:
                data, addr = s.recvfrom(1024)
                if addr[0] not in gui.server_listbox.get(0, tk.END):
                    gui.log(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - 发现服务器: {addr[0]}')
                    gui.server_listbox.insert(tk.END, addr[0])
            except socket.timeout:
                break

def tcp_client(gui, host, port, message):
    retries = gui.retry_attempts.get()
    while retries > 0:
        try:
            if gui.socket is None:
                gui.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if gui.ssl_enabled.get():
                    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                    gui.socket = context.wrap_socket(gui.socket, server_hostname=host)
                gui.socket.settimeout(gui.connection_timeout.get())
                gui.socket.connect((host, port))
                gui.log(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - 已连接到 {host}:{port}')
            msg = zlib.compress(message.encode()) if gui.compression_enabled.get() else message.encode()
            gui.socket.sendall(msg[:gui.packet_size.get()])
            data = gui.socket.recv(gui.packet_size.get())
            data = zlib.decompress(data).decode() if gui.compression_enabled.get() else data.decode()
            if "error" in data.lower():
                raise Exception("服务器错误： " + data)
            gui.log(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - 目標{data}')
            break
        except (socket.timeout, socket.error, Exception) as e:
            gui.log(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - 错误: {str(e)}')
            retries -= 1
            if gui.socket:
                gui.socket.close()
                gui.socket = None
        if retries == 0:
            gui.log("重试次数已用完，无法连接到服务器。")

class TCPClientGUI:
    def __init__(self, root):
        self.root, self.socket = root, None
        self.root.title("TCP 客户端")
        self.root.geometry("1000x600")
        self.root.minsize(800, 600)
        self.ssl_enabled, self.compression_enabled, self.heartbeat_enabled, self.reconnect_enabled = tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar()
        self.connection_timeout, self.packet_size, self.log_level = tk.DoubleVar(value=10.0), tk.IntVar(value=1024), tk.StringVar(value="INFO")
        self.retry_attempts, self.max_connections, self.keep_alive_time = tk.IntVar(value=3), tk.IntVar(value=10), tk.DoubleVar(value=60.0)
        self.image_path = tk.StringVar()
        self.bg_color = tk.StringVar()
        self.bg_image, self.bg_label = None, tk.Label(self.root)
        self.bg_label.place(relwidth=1, relheight=1)
        self.style = ttkb.Style()
        self.root.bind("<Configure>", self.resize)
        self._create_widgets()
        self._create_notebook()
        show_about(self.about_frame)

    def _create_widgets(self):
        self.host_label = ttkb.Label(self.root, text="主机:")
        self.host_label.grid(column=0, row=0, padx=5, pady=5, sticky="e")
        self.host_entry = ttkb.Entry(self.root)
        self.host_entry.grid(column=1, row=0, padx=5, pady=5, sticky="ew")
        self.host_entry.bind('<Return>', lambda e: self.port_entry.focus_set())
        self.port_label = ttkb.Label(self.root, text="端口:")
        self.port_label.grid(column=2, row=0, padx=5, pady=5, sticky="e")
        self.port_entry = ttkb.Entry(self.root)
        self.port_entry.grid(column=3, row=0, padx=5, pady=5, sticky="ew")
        self.connect_button = ttkb.Button(self.root, text="连接", command=self.connect_server, bootstyle="primary")
        self.connect_button.grid(column=4, row=0, padx=5, pady=5, sticky="ew")
        self.search_button = ttkb.Button(self.root, text="搜索服务器", command=self.search_servers, bootstyle="info")
        self.search_button.grid(column=5, row=0, padx=5, pady=5, sticky="ew")
        self.server_listbox = tk.Listbox(self.root, height=10)
        self.server_listbox.grid(column=0, row=1, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.server_listbox.bind('<<ListboxSelect>>', self.on_server_select)
        self.output_text = tk.Text(self.root, height=10)
        self.output_text.grid(column=3, row=1, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.message_frame = ttkb.LabelFrame(self.root, text="消息")
        self.message_frame.grid(column=0, row=2, columnspan=6, padx=5, pady=5, sticky="ew")
        self.message_entry = ttkb.Entry(self.message_frame)
        self.message_entry.grid(column=0, row=0, padx=5, pady=5, sticky="ew")
        self.message_entry.bind('<Return>', self.send_message)
        self.send_button = ttkb.Button(self.message_frame, text="发送", command=self.send_message, bootstyle="success")
        self.send_button.grid(column=1, row=0, padx=5, pady=5, sticky="ew")

    def _create_notebook(self):
        self.notebook = ttkb.Notebook(self.root, bootstyle="primary")
        self.notebook.grid(column=0, row=3, columnspan=6, padx=5, pady=5, sticky="nsew")
        self.settings_frame = ttkb.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="设置")
        self.advanced_settings_frame = ttkb.Frame(self.notebook)
        self.notebook.add(self.advanced_settings_frame, text="高级设置")
        self.professional_settings_frame = ttkb.Frame(self.notebook)
        self.notebook.add(self.professional_settings_frame, text="专业设置")
        self.emergency_frame = ttkb.Frame(self.notebook)
        self.notebook.add(self.emergency_frame, text="应急处理")
        self.about_frame = ttkb.Frame(self.notebook)
        self.notebook.add(self.about_frame, text="关于")
        show_settings(self.settings_frame, [("上传图片路径:", self.image_path)], "设置")
        ttkb.Button(self.settings_frame, text="选择图片", command=self.choose_bg_image, bootstyle="secondary").grid(row=2, columnspan=2, padx=10, pady=5)
        ttkb.Button(self.settings_frame, text="选择颜色", command=self.choose_bg_color, bootstyle="secondary").grid(row=3, columnspan=2, padx=10, pady=5)
        ttkb.Label(self.settings_frame, text="日志类型:").grid(row=4, column=0, padx=10, pady=5, sticky='e')
        self.log_type = ttkb.Combobox(self.settings_frame, textvariable=self.log_level, values=["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_type.grid(row=4, column=1, padx=10, pady=5, sticky='w')
        advanced_settings = [("启用SSL/TLS加密", self.ssl_enabled), ("启用数据压缩", self.compression_enabled), ("启用心跳机制", self.heartbeat_enabled), ("启用自动重连", self.reconnect_enabled)]
        show_settings(self.advanced_settings_frame, advanced_settings, "高级设置")
        professional_settings = [
            ("连接超时 (秒):", self.connection_timeout), ("数据包大小 (字节):", self.packet_size),
            ("重试次数:", self.retry_attempts), ("最大连接数:", self.max_connections), ("保持连接时间 (秒):", self.keep_alive_time)
        ]
        for i, (text, var) in enumerate(professional_settings):
            ttkb.Label(self.professional_settings_frame, text=text).grid(row=i, column=0, sticky='e', padx=10, pady=5)
            ttkb.Entry(self.professional_settings_frame, textvariable=var).grid(row=i, column=1, sticky='w', padx=10, pady=5)
        ttkb.Button(self.emergency_frame, text="中断连接", command=self.close_connection, bootstyle="danger").pack(padx=10, pady=5, fill=tk.BOTH)
        ttkb.Button(self.emergency_frame, text="重新连接服务器", command=self.connect_server, bootstyle="warning").pack(padx=10, pady=5, fill=tk.BOTH)
        ttkb.Button(self.emergency_frame, text="kill 应用", command=self.kill_app, bootstyle="danger").pack(padx=10, pady=5, fill=tk.BOTH)
        ttkb.Button(self.emergency_frame, text="重启应用", command=self.restart_app, bootstyle="warning").pack(padx=10, pady=5, fill=tk.BOTH)

    def connect_server(self):
        host, port = self.host_entry.get(), int(self.port_entry.get())
        threading.Thread(target=self.threaded_connect, args=(host, port)).start()

    def threaded_connect(self, host, port):
        try:
            if self.socket is None:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if self.ssl_enabled.get():
                    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                    self.socket = context.wrap_socket(self.socket, server_hostname=host)
                self.socket.settimeout(self.connection_timeout.get())
                self.socket.connect((host, port))
                self.log(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - 已连接到 {host}:{port}')
        except Exception as e:
            self.log(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - 错误: {str(e)}')
            if self.socket:
                self.socket.close()
                self.socket = None

    def search_servers(self):
        self.log("开始搜索服务器...")
        threading.Thread(target=discover_servers, args=(self,)).start()

    def on_server_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self.host_entry.delete(0, tk.END)
            self.host_entry.insert(0, event.widget.get(index))
            self.log(f"选择服务器: {event.widget.get(index)}")
            self.port_entry.focus_set()

    def send_message(self, event=None):
        if self.socket is None:
            messagebox.showwarning("警告", "请先连接到服务器！")
            return
        message = self.message_entry.get()
        if not message.strip():
            messagebox.showwarning("警告", "消息不能为空！")
            return
        host, port = self.host_entry.get(), int(self.port_entry.get())
        self.log(f"发送消息到 {host}:{port}: {message}")
        self.message_entry.delete(0, tk.END)
        self.message_entry.config(state=tk.DISABLED)
        threading.Thread(target=self.threaded_send, args=(host, port, message)).start()

    def threaded_send(self, host, port, message):
        tcp_client(self, host, port, message)
        self.root.after(0, self.unlock_message_entry)
        
    def unlock_message_entry(self):
        self.message_entry.config(state=tk.NORMAL)
        self.message_entry.focus()

    def close_connection(self):
        if self.socket:
            self.socket.close()
            self.socket = None
            self.log("连接已关闭。")

    def kill_app(self):
        self.log("应用将被kill。")
        os._exit(0)

    def restart_app(self):
        self.log("应用将重启。")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def scroll_to_bottom(self):
        self.output_text.see(tk.END)

    def log(self, message):
        self.output_text.insert(tk.END, f"{message}\n")
        self.scroll_to_bottom()

    def choose_bg_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.image_path.set(file_path)
            self.bg_image = Image.open(file_path)
            self.update_bg_image()

    def choose_bg_color(self):
        color_code = colorchooser.askcolor(title="选择背景颜色")
        if color_code:
            self.bg_color.set(color_code[1])
            self.root.config(bg=color_code[1])

    def update_bg_image(self):
        if self.bg_image:
            width, height = self.root.winfo_width(), self.root.winfo_height()
            resized_image = self.bg_image.resize((width, height), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(resized_image)
            self.bg_label.config(image=self.bg_photo)

    def resize(self, event):
        self.update_bg_image()

if __name__ == "__main__":
    try:
        root = ThemedTk(theme="superhero")
        app = TCPClientGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")
