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

def Registration(conn, addr):
    fileAccountWrite = open('ListAccount.txt', 'a')
    try:
        while True:
            fileAccountRead = open('ListAccount.txt', 'r')
            msgCheck = conn.recv(1024).decode("utf8")
            if msgCheck == "break":
                return
            usernameRecv = conn.recv(1024).decode("utf8")
            passwordRecv = conn.recv(1024).decode("utf8")
            passwordRepRecv = conn.recv(1024).decode("utf8")
            check_exist = usernameRecv
            success = True
            while fileAccountRead.tell() != os.fstat(fileAccountRead.fileno()).st_size:
                line = fileAccountRead.readline()
                line_split = line.split(" ")

                if line_split[0] == usernameRecv or passwordRepRecv != passwordRecv:
                    conn.sendall(bytes("Passwords aren't the same", "utf8"))
                    success = False
                    break
            if success == True:
                fileAccountWrite.writelines(usernameRecv + " " + passwordRecv + "\n")
                conn.sendall(bytes("Account created successfully", "utf8"))
                break
        fileAccountRead.close()
        fileAccountWrite.close()
    except socket.error:
        return

def LogIn(conn, addr):
    while True:
        try:
            fileAccountRead = open('ListAccount.txt', 'r')
            msgCheck = conn.recv(1024).decode("utf8")
            if msgCheck == "break":
                return
            usernameRecv = conn.recv(1024).decode("utf8")
            passwordRecv = conn.recv(1024).decode("utf8")
            print("LAY XONG ROI NE")
            success = False
            while fileAccountRead.tell() != os.fstat(fileAccountRead.fileno()).st_size:
                line = fileAccountRead.readline()
                if line == usernameRecv + " " + passwordRecv + "\n":
                    conn.sendall(bytes("Login successfully", "utf8"))
                    success = True
                    fileAccountRead.close()
                    break
            if success == False:
                conn.sendall(bytes("Account doesn't exist", "utf8"))
            else:
                break
        except socket.error:
            return


def updateFileData():
    #Lấy api_key một cách tự động do sau 15 ngày sẽ phải cập nhật.
    urlGetAPI = "https://vapi.vnappmob.com/api/request_api_key?scope=exchange_rate"
    resGet = req.get(urlGetAPI)
    #Tách kết quả lấy API.
    apiKey = resGet.text[12:(len (resGet.text) - 3)]

    url = "https://vapi.vnappmob.com/api/v2/exchange_rate/vcb"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    headers["Authorization"] = "Bearer " + apiKey

    r = requests.get(url, headers=headers)
    r = r.text.encode("utf-8")  #Dữ liệu text kiểu binary
    data = json.loads(r)    #Chuyển từ file json sang python

    #Ghi file binary
    file_data = open("data.json", "wb")
    file_data.write(r)
    file_data.close()


#Tự động cập nhập sau 30 phút
def updateFileDataAfter30():
    schedule.every(30).minutes.do(updateFileData)
    while 1:
        schedule.run_pending()
        time.sleep(1)


# Nếu mà tìm kiếm khác ngày hôm nay thì phải ghi dữ liệu vào 1 file khác và request

def findInforCurrency(currency):
    fileDataRead = "data.json"
    f = open(fileDataRead, "r", encoding='utf-8-sig')
    data = json.load(f)
    checkFind = False
    try:
        counter = 0
        while counter < 20:
            currencyData = str(data["results"][counter]["currency"])
            if (currencyData == currency):
                    checkFind = True
                    replyClient = {"buy_cash":data["results"][counter]["buy_cash"] ,
                            "buy_transfer":data["results"][counter]["buy_transfer"],
                            "currency":currency,
                            "sell":data["results"][counter]["sell"]}
                    #Chuyển về kiểu bytes để gửi về cho client.
                    inforCurrency = json.dumps(replyClient).encode('utf-8')
                    conn.send(inforCurrency)
                    break
            counter = counter + 1

        if checkFind == False:
            replyClient = {"id": -1} # tin nhắn không thành công format json
            findError = pickle.dumps(replyClient)
            conn.send(findError)
        #ĐOẠN NÀY XEM NÊN CẦU THIẾT KHÔNG
        else:
            check = {"id": 0}
            success = pickle.dumps(check)
            conn.send(success)
        f.close()
        return
    except socket.error:
        return


def LookUp(conn, addr):
    while True:
        try:
            msgClient = conn.recv(1024).decode("utf8")   #lấy yêu cầu tra cứu hay thoát clien
            if msgClient == "stop lookup":   # "dung tra cuu"
                return
            
            msgCurrency = conn.recv(1024).decode("utf8")
            findInforCurrency(msgCurrency)
        except socket.error:
            return


def clientExit(conn, addr):
    conn.close()
    print(f"{addr} da thoat khoi server")


def requestClient(conn, addr):
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
        if command == "register":     #"dang ky"
            Registration(conn, addr)
        elif command == "login":   #"dang nhap"
            LogIn(conn, addr)
        elif command == "lookup":     #"tra cuu"
            LookUp(conn, addr)
        elif command == "exit":
            clientExit(conn, addr)
            break

# --------------------------- main ------------------------------------

hostName = socket.gethostname()
HOST = socket.gethostbyname(hostName)
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
        t2 = threading.Thread(target=updateFileDataAfter30, args=())
        t2.start()
        print('Waiting for client')
        conn, addr = s.accept()
        print(f"{addr} da ket noi den server")
        print(f"Handle client: {addr}")
        # run in separated thread - many clients can connect
        t = threading.Thread(target=requestClient, args=(conn, addr))
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
