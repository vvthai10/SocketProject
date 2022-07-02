import socket
import tkinter as tk       
import threading
from tkinter import ttk
from tkinter import *
from PIL import  Image,ImageTk
import threading
import os
import requests
import json
import schedule
import requests as req
from datetime import datetime
from threading import Thread
from queue import Queue
import threading
from requests.structures import CaseInsensitiveDict 
from urllib.request import urlopen

#Global variable
queue = Queue()                 #Use get information and print on UI server.
updateFile30 = False            #Use check use function "updateFileData" normal or use update after 30 minutes.
#======================================FUNCTION===============================================
#@DESCR: Get date first in file data.
#@PARAM: None
#@RETURN: day, month, year.
def getDateFirst():
    filename = "data.json"
    f = open(filename, "r", encoding='utf-8-sig')
    data = json.load(f)
    
    inforFirst = list(data.keys())[0]

    day = inforFirst[7 : 9]
    month = inforFirst[9 : 11]
    year = inforFirst[11 : 15]
   
    f.close()
    return day, month, year
#@DESCR: Check registration when user send request and check account is correct.
#@PARAM: conn(Use send information to user.), addr(IP - PORT)
#@RETURN: result successful or unsuccessful.
def Registration(conn, addr):
    fileAccountWrite = open('ListAccount.txt', 'a')             #Read file account of Server.
    try:
        while True:
            fileAccountRead = open('ListAccount.txt', 'r')
            #Check user want continue or break
            msgCheck = conn.recv(1024).decode("utf8")
            if msgCheck == "break":
                return
            #Get infor registration of user send.
            inforRegis_String = conn.recv(1024).decode("utf8")
            inforRegis_Dict = json.loads(inforRegis_String)
            usernameRecv = inforRegis_Dict["account"]
            passwordRecv = inforRegis_Dict["password"]
            passwordRepRecv = inforRegis_Dict["password_rep"]
            
            #Check account is correct.
            success = True
            while fileAccountRead.tell() != os.fstat(fileAccountRead.fileno()).st_size:
                line = fileAccountRead.readline()
                line_split = line.split(" ")
                #Check account is exist and password, password reply have equal.
                if line_split[0] == usernameRecv or passwordRepRecv != passwordRecv:
                    addrList = list(addr)
                    addrList.append("User registered with incorrect password re-entered.")
                    queue.put(addrList)
                    print(str(addrList[0]) + "-" + str(addrList[1]) + " User registered with incorrect password re-entered.")
                    
                    conn.sendall(bytes("Passwords aren't the same", "utf8"))
                    success = False
                    break
            #Registration is successful.
            if success == True:
                fileAccountWrite.writelines(usernameRecv + " " + passwordRecv + "\n")
                addrList = list(addr)
                addrList.append("User successfully registered for an account.")
                queue.put(addrList)
                print(str(addrList[0]) + "-" + str(addrList[1]) + " User successfully registered for an account.")
                
                conn.sendall(bytes("Account created successfully", "utf8"))
                break
        fileAccountRead.close()
        fileAccountWrite.close()
    except socket.error:
        return
#@DESCR: Check login when user send request and check account is correct.
#@PARAM: conn(Use send information to user.), addr(IP - PORT)
#@RETURN: result successful or unsuccessful.
def LogIn(conn, addr):
    while True:
        try:
            fileAccountRead = open('ListAccount.txt', 'r')
            msgCheck = conn.recv(1024).decode("utf8")
            if msgCheck == "break":
                return
            
            inforUser_String = conn.recv(1024).decode("utf8")
            inforUser_Dict = json.loads(inforUser_String)
            usernameRecv = inforUser_Dict["account"]
            passwordRecv = inforUser_Dict["password"]
            
            success = False
            while fileAccountRead.tell() != os.fstat(fileAccountRead.fileno()).st_size:
                line = fileAccountRead.readline()
                if line == usernameRecv + " " + passwordRecv + "\n":
                    addrList = list(addr)
                    addrList.append("User successfully login for an account.")
                    queue.put(addrList)
                    print(str(addrList[0]) + "-" + str(addrList[1]) + " User successfully login for an account.")
                    
                    conn.sendall(bytes("Login successfully", "utf8"))
                    
                    day, month, year = getDateFirst()
                    conn.sendall(bytes(day, "utf8"))
                    conn.sendall(bytes(month, "utf8"))
                    conn.sendall(bytes(year, "utf8"))
                    #======================================
                    success = True
                    fileAccountRead.close()
                    break
            if success == False:
                addrList = list(addr)
                addrList.append("User unsuccessful login for an account.")
                queue.put(addrList)
                print(str(addrList[0]) + "-" + str(addrList[1]) + " User unsuccessful login for an account.")
                    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                conn.sendall(bytes("Account doesn't exist", "utf8"))
            else:
                break
        except socket.error:
            return
#@DESCR: Write in file data.
#@PARAM: None.
#@RETURN: None.
def updateFileData():
    global updateFile30
    #Get api key(because it is auto update after 15 days).
    url_get_api_key = "https://vapi.vnappmob.com/api/request_api_key?scope=exchange_rate"
    response = urlopen(url_get_api_key)
    resp = json.loads(response.read())
    api_key = resp["results"]

    #Get information when has api key.
    url = "https://vapi.vnappmob.com/api/v2/exchange_rate/vcb"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer " + api_key
    
    r = requests.get(url, headers=headers)
    r = r.text.encode("utf-8")  
    dataNew = json.loads(r)    

    #Add date in result of information.
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    nameChange = "results" + day + month + year

    #Start write in file data.
    filename = "data.json"  
    f = open(filename, "r", encoding='utf-8-sig')
    data = json.load(f)
    dataNew[nameChange] = dataNew. pop("results")
    #Check file is empty(file have {} or []).
    if (str(data) == '{}' or str(data) == '[]'):
        json_object = json.dumps(dataNew, indent = 4)
        with open("data.json", "w") as outfile:
            outfile.write(json_object)
    else:
        data.update(dataNew)
        json_object = json.dumps(data, indent = 4)
        with open("data.json", "w") as outfile:
            outfile.write(json_object)
    #If function use update after 30 minutes, print infomation on UI Server.
    if updateFile30 == True:
        addrList = ["", ""]
        addrList.append("Server self-updated data today.")
        queue.put(addrList)
        print("Server self-updated data today.")
        updateFile30 = False
#@DESCR: Auto update after 30 minutes.
#@PARAM: None.
#@RETURN: None.
def updateFileDataAfter30():
    schedule.every(30).minutes.do(updateFileData)
    while 1:
        global updateFile30
        updateFile30 = True
        schedule.run_pending()
#@DESCR: Check result need lookup when user request.
#@PARAM: currency, day, month, year, conn, addr.
#@RETURN: result or notification don't lookup.
def findInforCurrency(currency, day, month, year, conn, addr):
    fileDataRead = "data.json"
    f = open(fileDataRead, "r", encoding='utf-8-sig')
    data = json.load(f)
    checkFind = False
    nameFind = "results" + day + month + year
    try:
        if nameFind in data.keys():
            counter = 0
            while counter < 20:
                currencyData = str(data[nameFind][counter]["currency"])
                if (currencyData == currency):
                        checkFind = True
                        replyClient = {"buy_cash":data[nameFind][counter]["buy_cash"] ,
                                "buy_transfer":data[nameFind][counter]["buy_transfer"],
                                "currency":currency,
                                "sell":data[nameFind][counter]["sell"]}
                        #Change types to Bytes
                        inforCurrency = json.dumps(replyClient).encode('utf-8')
                        #=======================================================
                        addrList = list(addr)
                        date_S = day + "/" + month + "/" + year
                        data_Queue = "The server sends results to the user about currency information " + currencyData + " on date: " + date_S + "."
                        addrList.append(data_Queue)
                        queue.put(addrList)
                        print(str(addrList[0]) + "-" + str(addrList[1]) + " " + data_Queue)
                    
                        conn.send(inforCurrency)
                        break
                counter = counter + 1
        
        if checkFind == False:
            replyClient = {"id": -1}            #Send message form dictionary.
            noteError = json.dumps(replyClient).encode('utf-8')
            #=======================================================
            addrList = list(addr)
            data_Queue = "The time the user requested no data. Please check the time again."
            addrList.append(data_Queue)
            queue.put(addrList)
            print(str(addrList[0]) + "-" + str(addrList[1]) + " " + data_Queue)
            
            conn.send(noteError)       
        else:
            check = {"id": 0}
            noteError = json.dumps(check).encode('utf-8')
            #=======================================================
            
            conn.send(noteError)
        f.close()
        return
    except socket.error:
        return
#@DESCR: Wait look user send request about currency and date lookup.
#@PARAM: conn, addr.
#@RETURN: None.
def LookUp(conn, addr):
    while True:
        try:            
            msgClient = conn.recv(1024).decode("utf8")  
            if msgClient == "stop lookup": 
                return

            inforLoopup_String = conn.recv(1024).decode("utf8")
            inforUser_Dict = json.loads(inforLoopup_String)
            msgCurrency = inforUser_Dict["currency"]
            msgDay = inforUser_Dict["day"]
            msgMonth = inforUser_Dict["month"]
            msgYear = inforUser_Dict["year"]
            
            addrList = list(addr)
            date_S = msgDay + "/" + msgMonth + "/" + msgYear
            data_Queue = "The server receives a request to look up information about the currency " + msgCurrency + " on date: " + date_S + "."
            addrList.append(data_Queue)
            queue.put(addrList)
            print(str(addrList[0]) + "-" + str(addrList[1]) + " " + data_Queue)
            #Start loopup when get information.
            findInforCurrency(msgCurrency, msgDay, msgMonth, msgYear, conn, addr)
        except socket.error:
            return
#@DESCR: Client want exit.
#@PARAM: conn, addr.
#@RETURN: None.
def clientExit(conn, addr):
    addrList = list(addr)
    addrList.append("User has exited the server")
    queue.put(addrList)
    conn.close()
    print(str(addrList[0]) + "-" + str(addrList[1]) + " User has exited the server")
#@DESCR: Server wait get information user request.
#@PARAM: conn, addr.
#@RETURN: function follow request user.
def requestClient(conn, addr):
    while True:
        try:
            command = conn.recv(1024).decode("utf8")
        except:
            addrList = list(addr)
            addrList.append("User exited unexpectedly.")
            queue.put(addrList)
            print(str(addrList[0]) + "-" + str(addrList[1]) + ' User exited unexpectedly')
            conn.close()
            break

        command = command.lower()
        addrList = list(addr)
        addrList.append('User wants to ' + str(command))
        queue.put(addrList)
        print(str(addrList[0]) + "-" + str(addrList[1]) + ' User wants to: ', command)
        if command == "register":    
            Registration(conn, addr)
        elif command == "login":   
            LogIn(conn, addr)
        elif command == "lookup": 
            LookUp(conn, addr)
        elif command == "exit":
            clientExit(conn, addr)
            break
#@DESCR: Server wait connect user when user request connect.
#@PARAM: None.
#@RETURN: None.
def severLoop():
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
            data = 'Waiting for client'
            print(data)
            conn, addr = s.accept()
            
            #Put in queue.
            addrList = list(addr)
            addrList.append('User sends connection request to server.')
            queue.put(addrList)
            print(str(addrList[0]) + "-" + str(addrList[1]) + " User sends connection request to server.")
            addrList = list(addr)
            addrList.append("User connected to the server")
            queue.put(addrList)
            print(str(addrList[0]) + "-" + str(addrList[1]) + " User connected to the server.")
            # Use thread to run function get request and Server again wait user connect.
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

#Get ip of server.
hostName = socket.gethostname()
HOST = socket.gethostbyname(hostName)
PORT = 65432
#@DESCR: UI of server.
#@PARAM: None.
#@RETURN: None.
class Application(tk.Frame):              
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()                    
        self.createWidgets()

    def printInformation(self):
        while(1):
            while(queue.empty() != True):
                data = queue.get()
                self.tree.insert(parent='', index='end', text = "" , values=(data))
    

    def createWidgets(self):   
        #self.printButton = tk.Button(self, text='Load',command=lambda: self.printInformation())         
        #self.printButton.grid(row=1,column=0) 
        printInfo = threading.Thread(target=self.printInformation)   # gui thread
        printInfo.daemon = True  # background thread will exit if main thread exits
        printInfo.start()
        self.msgWarning = tk.Label(self, font=("Arial", 25), text = "SERVER CURRENCY CONVERSION: " + HOST)
        self.msgWarning.place(anchor = 'center')
        self.msgWarning.grid(row = 0, column = 0)
        
        self.tree = ttk.Treeview(self, selectmode = 'browse', height=15)
        self.tree.place(x = 30, y = 95)

        self.vsb = ttk.Scrollbar(self, orient = "vertical", command = self.tree.yview)
        self.vsb.place(x = 1060, y = 94, height = 200 + 20)

        self.tree.configure(yscrollcommand = self.vsb.set)

        self.tree["columns"] = ('ip', 'port', 'request')
        self.tree['show'] = 'headings'
        self.tree.column("ip", width = 200, anchor = 'c')
        self.tree.column("port", width = 200, anchor = 'c')
        self.tree.column("request", width = 680, anchor = 'c')
        self.tree.heading("ip", text = "IP")
        self.tree.heading("port", text = "Port")
        self.tree.heading("request", text = "Request")
        self.tree.grid(row=5, column=0, sticky='nsew')
#@DESCR: Run UI of server.
#@PARAM: None.
#@RETURN: None.
def runtk():
    app = Application()     
    app.master.geometry("1080x400")                   
    app.master.title('SERVER CURRENCY')   
    app.master.iconbitmap('dollar.ico')
    app.mainloop()


#====================MAIN========================
thd = threading.Thread(target=runtk)  
thd.daemon = True  #Background thread will exit if main thread exits
thd2 = threading.Thread(target=severLoop) 
thd2.daemon = True  #Background thread will exit if main thread exits
thd.start()  # start tk loop
thd2.start()

thd.join()  # start tk loop
thd2.join()

queue.join()