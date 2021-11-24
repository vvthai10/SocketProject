import socket
import threading
import os
import requests
import json
import pickle
import schedule
import time
import requests as req
from datetime import datetime
from requests.structures import CaseInsensitiveDict 
# --- functions ---

def dang_ky(conn, addr):
    file_registry = open('DS_ng_dung.txt', 'a')
    try:
        while True:
            file_read = open('DS_ng_dung.txt', 'r')
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
                    conn.sendall(bytes("Ten dang nhap ton tai", "utf8"))
                    success = False
                    break
            if success == True:
                file_registry.writelines(username_recv + " " + password_recv + "\n")
                conn.sendall(bytes("Dang ky thanh cong", "utf8"))
                break
        file_read.close()
        file_registry.close()
    except socket.error:
        return


def dang_nhap(conn, addr):
    while True:
        try:
            file_Login = open('DS_ng_dung.txt', 'r')
            msg_check = conn.recv(1024).decode("utf8")
            if msg_check == "break":
                return
            user_name = conn.recv(1024).decode("utf8")
            password = conn.recv(1024).decode("utf8")
            success = False
            while file_Login.tell() != os.fstat(file_Login.fileno()).st_size:
                line = file_Login.readline()
                if line == user_name + " " + password + "\n":
                    conn.sendall(bytes("Ban da dang nhap thanh cong", "utf8"))
                    success = True
                    file_Login.close()
                    break
            if success == False:
                conn.sendall(bytes("Ten dang nhap hoac mat khau khong dung", "utf8"))
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
    file_data = open("data.json", "wb")
    file_data.write(r)
    file_data.close()


def update_json_data_after_30m():
    schedule.every(30).minutes.do(update_json_file)
    while 1:
        schedule.run_pending()
        time.sleep(1)


# Nếu mà tìm kiếm khác ngày hôm nay thì phải ghi dữ liệu vào 1 file khác và request

def tra_cuu_implement(money):
    print("Vo cho doc file de tra")
    filename = "data.json"
    f = open(filename, "r", encoding='utf-8-sig')
    data = json.load(f)
    flag = False
    print("BUOC TRA TRONG FILE JSON")
    try:
        counter = 0
        while counter < 20:
            s = str(data["results"][counter]["currency"])
            print(s)
            if (s == money):
                    flag = True
                    reply = {"buy_cash":data["results"][counter]["buy_cash"] ,
                            "buy_transfer":data["results"][counter]["buy_transfer"],
                            "currency":money,
                            "sell":data["results"][counter]["sell"]}
                    print(reply)
                    res_bytes = json.dumps(reply).encode('utf-8')
                    print("GUI VE CHO CLIENT")
                    conn.send(res_bytes)
                    break
            counter = counter + 1

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
    print("Toi cho bat dau nhan thong tin tra")
    while True:
        try:
            msg = conn.recv(1024).decode("utf8")   #lấy yêu cầu tra cứu hay thoát clien
            print("BIEN MSG: ")
            print(msg)
            if msg == "dung tra cuu":
                return
            
            print("Chuan bi lay xem m gui gi cho server")
            msg_money = conn.recv(1024).decode("utf8")
            #conn.recv(1024).decode("utf8")  #Thông tin loại tiền mà client yêu câuf
            print("Tien hanh tra:  ")
            print(msg_money)
            tra_cuu_implement(msg_money)
            print("DA QUAY VE HAM TRA CUU")
        except socket.error:
            return


def client_exit(conn, addr):
    conn.close()
    print(f"{addr} da thoat khoi server")


def handle_client(conn, addr):
    while True:
        print('[handle_client] read command')

        try:
            command = conn.recv(1024).decode("utf8")
        except:
            print(f'{addr} đã thoát 1 cách đột ngột')
            conn.close()
            break

        command = command.lower()
        print('[handle_client] run command:', command)
        if command == "dang ky":
            dang_ky(conn, addr)
        elif command == "dang nhap":
            dang_nhap(conn, addr)
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
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
             1)
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
