import socket
import threading
import os
import requests
import json
import pickle
import schedule
import time
from datetime import datetime
from requests.structures import CaseInsensitiveDict  #sử dụng cái hàm headers["Accept"], headers["Authorization"]
# --- functions ---

def Registration(conn, addr):
    file_registry = open('InforUser.txt', 'a')
    try:
        while True:
            file_read = open('InforUser.txt', 'r')
            msg_check = conn.recv(1024).decode("utf8")
            if msg_check == "break":
                return
            username_recv = conn.recv(1024).decode("utf8")
            password_recv = conn.recv(1024).decode("utf8")
            pass_again_recv = conn.recv(1024).decode("utf8")
            check_exist = username_recv
            success = True
            while file_read.tell() != os.fstat(file_read.fileno()).st_size:
                line = file_read.readline()
                line_split = line.split(" ")

                if line_split[0] == check_exist or pass_again_recv != password_recv:
                    conn.sendall(bytes("Tài khoản đã tồn tại", "utf8"))
                    success = False
                    break
            if success == True:
                file_registry.writelines(username_recv + " " + password_recv + "\n")
                conn.sendall(bytes("Đăng kí thành công", "utf8"))
                break
        file_read.close()
        file_registry.close()
    except socket.error:
        return


def Login(conn, addr):
    while True:
        try:
            file_Login = open('InforUser.txt', 'r')
            msg_check = conn.recv(1024).decode("utf8")
            if msg_check == "break":
                return
            user_name = conn.recv(1024).decode("utf8")
            password = conn.recv(1024).decode("utf8")
            success = False
            while file_Login.tell() != os.fstat(file_Login.fileno()).st_size:
                line = file_Login.readline()
                if line == user_name + " " + password + "\n":
                    conn.sendall(bytes("Đăng nhập thành công", "utf8"))
                    success = True
                    file_Login.close()
                    break
            if success == False:
                conn.sendall(bytes("Tên đăng nhập hoặc mật khẩu không đúng", "utf8"))
            else:
                break
        except socket.error:
            return





def update_json_file():
    #Lấy api_key một cách tự động do sau 15 ngày sẽ phải cập nhật.
    url_get_api_key = "https://vapi.vnappmob.com/api/request_api_key?scope=exchange_rate"
    resp = req.get(url_get_api_key)
    api_key = resp.text[12:(len (resp.text) - 3)]

    url = "https://vapi.vnappmob.com/api/v2/exchange_rate/vcb"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    #api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MzgyMDIxMzYsImlhdCI6MTYzNjkwNjEzNiwic2NvcGUiOiJleGNoYW5nZV9yYXRlIiwicGVybWlzc2lvbiI6MH0.YS1yDCiew3Lo0tABSSlPpqTK_xHr_iQzGP3wHPJnPII"
    headers["Authorization"] = "Bearer " + api_key

    r = requests.get(url, headers=headers)
    r = r.text.encode("utf-8")  #Dữ liệu text kiểu binary
    data = json.loads(r)    #Chuyển từ file json sang python

    #Ghi file binary
    file_data = open("InforExchange.json", "wb")
    file_data.write(r)
    file_data.close()


def update_json_data_after_30m():
    schedule.every(30).minutes.do(update_json_file)
    while 1:
        schedule.run_pending()
        time.sleep(1)


def Luu_va_cap_nhat_du_lieu(nam, thang, ngay):
    url = 'https://tygia.com/json.php?ran=0&rate=0&gold=1&bank=VIETCOM&date=' + nam + thang + ngay

    r = requests.get(url)
    print('request thành công')
    r = r.text.encode("UTF8")
    data = json.loads(r)
    file_data = open('data1.json', 'wb')
    file_data.write(r)
    file_data.close()


# Nếu mà tìm kiếm khác ngày hôm nay thì phải ghi dữ liệu vào 1 file khác và request

def tra_cuu_implement(nam, thang, ngay, vang):
    today = datetime.today()
    date_search = datetime.strftime(today, "%Y-%m-%d")
    filename = "data.json"
    if nam + "-" + thang + "-" + ngay != date_search:
        filename = "data1.json"
        Luu_va_cap_nhat_du_lieu(nam, thang, ngay)
    f = open(filename, "r", encoding='utf-8-sig')
    infor = json.load(f)
    flag = False
    try:
        for name in infor['golds'][0]['value']:
            if name['company'] + " " + name['brand'] == vang or name['brand'] == vang:
                flag = True
                reply = pickle.dumps(name)
                conn.send(reply)

        if flag == False:
            flag_not_success = {"id": -1} # tin nhắn không thành công format json
            msg_not_success = pickle.dumps(flag_not_success)
            conn.send(msg_not_success)
        else:
            check = {"id": 0}
            success = pickle.dumps(check)
            conn.send(success)
        f.close()
        return
    except socket.error:
        return


def tra_cuu(conn, addr):
    while True:
        try:
            msg = conn.recv(1024).decode("utf8")
            if msg == "dung tra cuu":
                return
            msg_nam = conn.recv(1024).decode("utf8")
            msg_thang = conn.recv(1024).decode("utf8")
            msg_ngay = conn.recv(1024).decode("utf8")
            msg_vang = conn.recv(1024).decode("utf8")
            tra_cuu_implement(msg_nam, msg_thang, msg_ngay, msg_vang)
        except socket.error:
            return


def client_exit(conn, addr):
    conn.close()
    print(f"{addr} Da thoat khoi server")


def handle_client(conn, addr):
    while True:
        print('[handle_client] read command')

        try:
            command = conn.recv(1024).decode("utf8")
        except:
            print(f'{addr} Đã thoát 1 cách đột ngột')
            conn.close()
            break

        command = command.lower()
        print('[handle_client] run command:', command)
        if command == "dang ky":
            Registration(conn, addr)
        elif command == "dang nhap":
            Login(conn, addr)
        elif command == "tra cuu":
            tra_cuu(conn, addr)
        elif command == "exit":
            client_exit(conn, addr)
            break

# --------------------------- main ------------------------------------

host_name = socket.gethostname()
HOST = socket.gethostbyname(host_name)
print(HOST)
PORT = 65432

print('Starting ...')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen()

all_threads = []
all_clients = []
try:
    while True:
        t2 = threading.Thread(target=update_json_data_after_30m, args=())
        t2.start()
        print('Waiting for client')
        conn, addr = s.accept()
        print(f"{addr} da ket noi den server")
        print(f"Handle client: {addr}")
        # run in separated thread - many clients can connect
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.start()
        all_threads.append(t)
except KeyboardInterrupt:
    print('Stopped by Ctrl+C')
finally:
    s.close()
    for t in all_threads:
        t.join()
    for conn, addr in all_clients:
        conn.close()
