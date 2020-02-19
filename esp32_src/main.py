import socket
def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting...')
        wlan.connect('HeLuo', '11111111')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
do_connect()
port = 10001
s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0',port))  #绑定端口
from bsp import car_handler
print('listening.')
while True:         #接收数据
    data,addr=s.recvfrom(100)
    car_handler.receive_ascii(data)



