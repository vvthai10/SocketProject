import tkinter as tk
from tkinter import ttk
from tkinter import *
import tkinter.messagebox
import socket
import json
import pickle
from PIL import  Image,ImageTk
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# =============================FUNCTION============================

def connectToServer():
    HOST = entry.get()
    PORT = 65432
    test = True
    try:
        client.connect((HOST, PORT))
    except Exception as e:
        tkinter.messagebox.showerror(title="Error", message="Unable to connect to server.")
        test = False
    if test:
        tkinter.messagebox.showinfo(title="Notification", message="Connected to the server.")

def stopLookup(child_windown):
    msgRequest = "stop lookup"
    try:
        client.sendall(bytes(msgRequest, "utf8"))
    except socket.error:
        tkinter.messagebox.showinfo(title="Notification", message="Server closed connection.")
        client.close()
        root.destroy()
        return
    child_windown.destroy()


def LookUp(entry, tree, child_windown):
    try:
        isContinue = "continue"
        currency = entry.get()  #lấy thông tin loại tiền muốn tra cứu
        
        client.sendall(bytes(isContinue, "utf8"))
        client.sendall(bytes(currency, "utf8"))
    except socket.error:
        tkinter.messagebox.showinfo(title="Notification", message="Server closed connection.")
        client.close()
        root.destroy()
        return
    #Thực hiện nhiều lần yêu cầu của người dùng.
    i = 1
    while True:
        #3072
        resultServer = client.recv(1024)
        #Chuyển kết quả từ bytes sang kiểu dict
        
        result = json.loads(resultServer.decode('ISO-8859-1'))
        if result == {"id": 0}:
            break
        elif result == {"id": -1}:
            #HÌNH NHƯ MÌNH KHÔNG CẦN THÊM CÁI NÀY.
            tkinter.messagebox.showinfo("Thông báo","Tên này không tồn tại, hãy đảm bảo tên vàng bạn cần tìm là chính xác")
            break
        else:
            tree.insert(parent='', index='end', text="Item_" + str(i), 
                        values=(result['currency'], result['buy_cash'], result['buy_transfer'], result['sell']))
        i = i + 1

def dropDownList(window):
    OPTIONS = [
        "AUD",
        "CAD",
        "CHF",
        "CNY",
        "DKK",
        "EUR",
        "GBP",
        "HKD",
        "INR",
        "JPY",
        "KRW",
        "KWD",
        "MYR",
        "NOK",
        "RUB",
        "SAR",
        "SEK",
        "SGD",
        "THB",
        "USD"
    ] 
    variable = StringVar(window)
    variable.set(OPTIONS[0])
    menu = OptionMenu(window, variable, *OPTIONS)

    return [menu,variable]


def LookUpUI():
    msgRequest = "lookup"
    try:
        client.sendall(bytes(msgRequest, "utf8"))
    except socket.error:
        tkinter.messagebox.showinfo(title="Notification", message="Server closed connection.")
        client.close()
        root.destroy()
        return
    mainWindown = Toplevel(root)
    mainWindown.title("App")
    mainWindown.geometry("1200x300")
    columns = ('Money', 'buy_cash', 'buy_transfer', 'sell')
    tree = ttk.Treeview(mainWindown, columns=columns)
    tree.heading('#0', text='STT')
    tree.heading('#1', text='Currency')
    tree.heading('#2', text='Buy Cash')
    tree.heading('#3', text='Buy Transfer')
    tree.heading('#4', text='Sell')

    # Specify attributes of the columns
    tree.column('#0', stretch=tk.YES)
    tree.column('#1', stretch=tk.YES)
    tree.column('#2', stretch=tk.YES)
    tree.column('#3', stretch=tk.YES)
    tree.column('#4', stretch=tk.YES)
    tree.grid(row=5, columnspan=4, sticky='nsew')

    option = dropDownList(mainWindown)
    dropdown = option[0] # Đây là cái list tiền
    entry = option[1] # Đây là loại tiền mình muốn tra cứu
    buttonSearch = tk.Button(mainWindown, text='Lookup', command=lambda: LookUp(entry, tree, mainWindown))
    buttonExit = tk.Button(mainWindown, text="Exit", command=lambda: stopLookup(mainWindown))
    
    dropdownLabel = tk.Label(mainWindown, text = "Choose Currency")
    dropdownLabel.grid(row=2, column=1)
    dropdown.grid(row=2, column=2)
    buttonSearch.grid(row=3, column=2)
    buttonExit.grid(row=3, column=3)
    #     =====================================
    mainWindown.protocol("WM_DELETE_WINDOW", lambda: stopLookup(mainWindown))


def Registration(entry1, entry2, entry3, registerUI):
    try:
        client.sendall(bytes("continue", "utf8"))
        username = entry1.get()
        client.sendall(bytes(username, "utf8"))
        password = entry2.get()
        client.sendall(bytes(password, "utf8"))
        passwordRep = entry3.get()
        client.sendall(bytes(passwordRep, "utf8"))

        noticeServer = client.recv(1024).decode("utf8")
    except socket.error:
        tkinter.messagebox.showinfo(title="Notification", message="Server closed connection.")
        client.close()
        root.destroy()
        return
        #if noticeServer == "Account created successfully" and passwordRep == password:
    if noticeServer == "Account created successfully":
        tkinter.messagebox.showinfo(title="Notification", message="Account created successfully.")
        registerUI.destroy()
    elif noticeServer == "Passwords aren't the same":
        tkinter.messagebox.showerror(title="Error", message="Passwords aren't the same.")
    else:
        tkinter.messagebox.showerror(title="Error", message="Username available.")
        entry1.delete(0, 'end')
        entry2.delete(0, 'end')
        entry3.delete(0, 'end')


def Login(entry1, entry2, loginUI):
    try:
        client.sendall(bytes("continue", "utf8"))
        username = entry1.get()
        print(username)
        client.sendall(bytes(username, "utf8"))
        password = entry2.get()
        print(password)
        client.sendall(bytes(password, "utf8"))
        noticeServer = client.recv(1024).decode("utf8")
    except socket.error:
        tkinter.messagebox.showinfo(title="Notification", message="Server closed connection.")
        client.close()
        root.destroy()
        return
    if noticeServer == "Login successfully":
        tkinter.messagebox.showinfo(title="Notification", message="Login successfully.")
        loginUI.destroy()
        # Đăng nhập thành công thì được vào để tra cứu
        LookUpUI()
    else:
        tkinter.messagebox.showinfo(title="Error", message="Account doesn't exist.")
        entry1.delete(0, 'end')
        entry2.delete(0, 'end')


def isClose(userUI):
    client.sendall(bytes("break", "utf8"))
    userUI.destroy()


# =============Viết GUI cho đăng kí và đăng nhập=============
def RegistrationUI():
    msgRequest = "register"
    try:
        client.sendall(bytes(msgRequest, "utf8"))
    except socket.error:
        tkinter.messagebox.showinfo(title="Notification", message="Server closed connection.")
        client.close()
        root.destroy()
        return
    registerUI = Toplevel(root)
    entry1 = tk.Entry(registerUI, width=35)
    entry1.insert(0, 'Nhập tên đăng nhâp ')
    entry2 = tk.Entry(registerUI, show="*", width=35)
    entry2.insert(0, 'Nhập mật khẩu')
    entry3 = tk.Entry(registerUI, show="*", width=35)
    entry3.insert(0, 'Nhập lại mật khẩu')
    registerUI.geometry("300x300")
    registerUI.title("Đăng ký")
    entry1.grid(row=1, column=1)
    entry2.grid(row=2, column=1)
    entry3.grid(row=3, column=1)
    but_ok = tk.Button(registerUI, text="Đăng ký", command=lambda: Registration(entry1, entry2, entry3, registerUI))
    but_ok.grid(row=4, column=2)
    registerUI.protocol("WM_DELETE_WINDOW", lambda: isClose(registerUI))


def LoginUI():
    msgRequest = "login"
    try:
        client.sendall(bytes(msgRequest, "utf8"))
    except socket.error:
        tkinter.messagebox.showinfo(title="Notification", message="Server closed connection.")
        client.close()
        root.destroy()
        return
    loginUI = Toplevel(root)
    entry1 = tk.Entry(loginUI, width=35)
    entry1.insert(0, 'Nhập tên đăng nhâp ')
    entry2 = tk.Entry(loginUI, show="*", width=35)
    entry2.insert(0, 'Nhập mật khẩu')
    loginUI.geometry("300x300")
    loginUI.title("Đăng nhập")
    entry1.grid(row=1, column=1)
    entry2.grid(row=2, column=1)
    but_ok = tk.Button(loginUI, text="Đăng nhập", command=lambda: Login(entry1, entry2, loginUI))
    but_ok.grid(row=3, column=2)
    loginUI.protocol("WM_DELETE_WINDOW", lambda: isClose(loginUI))


def isExit():
    msgRequest = "exit"
    client.sendall(bytes(msgRequest, "utf8"))
    client.close()
    root.destroy()


# -------------main-----------------

root = tk.Tk()
root.geometry("900x500")
root.title("App")
img1=Image.open("gold_price.PNG")
test=ImageTk.PhotoImage(img1)
label1 = tkinter.Label(image=test)
label1.image = test
label1.place(x=1,y=1)

entry = tk.Entry()
entry.insert(0,'Nhập ip')
entry.grid(row=1, column=1)
myButton_connect = tk.Button(text="CONNECT", command=connectToServer)
myButton_connect.grid(row=1, column=2)
myButton_regis = tk.Button(text="REGISTER", command=RegistrationUI)
myButton_regis.grid(row=2, column=1)
myButton_login = tk.Button(text="LOGIN", command=LoginUI)
myButton_login.grid(row=3, column=1)
myButton_Exit = tk.Button(text="EXIT", command=isExit)
myButton_Exit.grid(row=5, column=1)
root.protocol("WM_DELETE_WINDOW", lambda: isExit())
root.mainloop()
