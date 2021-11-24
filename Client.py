# Cái điều khiển đó thì sau sửa lại. Cái đầu tiên vào là menu. Sau khi kích vào menu thì nó mới là câu lệnh bình thường
import tkinter as tk
from tkinter import ttk
from tkinter import *
import tkinter.messagebox
import socket
import pickle
from PIL import  Image,ImageTk
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# -------------func-------------

def ConnectToServer():
    HOST = entry.get()
    PORT = 65432
    test = True
    try:
        client.connect((HOST, PORT))
    except Exception as e:
        tkinter.messagebox.showerror(title="Lỗi", message="Lỗi kết nối đến server")
        test = False
    if test:
        tkinter.messagebox.showinfo(title="Thông báo", message="Đã kết nối tới server thành công")

def stop_tra_cuu(child_windown):
    msg = "dung tra cuu"
    try:
        client.sendall(bytes(msg, "utf8"))
    except socket.error:
        tkinter.messagebox.showinfo(title="Thông báo", message="Server đã đóng kết nối")
        client.close()
        root.destroy()
        return
    child_windown.destroy()


def tra_cuu(entry, tree, child_windown):
    print("MAY NHAN TIEN GI")
    print(entry)
    
    try:
        tiep_tuc = "tiep tuc"
        vang = entry.get()  #lấy thông tin loại tiền muốn tra cứu
        
        print("SAU KHI RUT DUOC GI TU ENTRY VAO VANG")
        print(vang)
        client.sendall(bytes(tiep_tuc, "utf8"))
        client.sendall(bytes(vang, "utf8"))
    except socket.error:
        tkinter.messagebox.showinfo(title="Thông báo", message="Server đã đóng kết nối")
        client.close()
        root.destroy()
        return
    i = 1
    print("CHUAN BỊ IN RA MAN HINH")
    while True:
        print("NHẬN THÔNG TIN GỬI VỀ")
        #3072
        result = client.recv(1024)
        print("IN THÔNG TIN GỬI VỀ")
        print(type(result))
        print(result)
        #Nhan duoc ket qua
        dist = pickle.loads(result)
        if dist == {"id": 0}:
            break
        elif dist == {"id": -1}:
            tkinter.messagebox.showinfo("Thông báo","Tên này không tồn tại, hãy đảm bảo tên vàng bạn cần tìm là chính xác")
            break
        else:
            print("Toi cho da tra ket qua")
            print(dist)
            tree.insert(parent='', index='end', text="Item_" + str(i), values=(
            dist['buy_cash'] + " " + dist['buy_transfer'], dist['currency'], dist['sell']))
        i = i + 1

def dropdownList(window):
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


def tra_cuu_w():
    msg = "tra cuu"
    try:
        client.sendall(bytes(msg, "utf8"))
    except socket.error:
        tkinter.messagebox.showinfo(title="Thông báo", message="Server đã đóng kết nối")
        client.close()
        root.destroy()
        return
    child_windown = Toplevel(root)
    child_windown.title("App")
    child_windown.geometry("1200x300")
    columns = ('Money', 'buy_cash', 'buy_transfer', 'sell')
    tree = ttk.Treeview(child_windown, columns=columns)
    tree.heading('#0', text='STT')
    tree.heading('#1', text='Money')
    tree.heading('#2', text='buy_cash')
    tree.heading('#3', text='buy_transfer')
    tree.heading('#4', text='sell')

    # Specify attributes of the columns
    tree.column('#0', stretch=tk.YES)
    tree.column('#1', stretch=tk.YES)
    tree.column('#2', stretch=tk.YES)
    tree.column('#3', stretch=tk.YES)
    tree.column('#4', stretch=tk.YES)
    tree.grid(row=5, columnspan=4, sticky='nsew')

    # add button
    #entry1 = tk.Entry(child_windown, width=15)
    #entry1.insert(0, 'năm')
    #entry2 = tk.Entry(child_windown, width=15)
    #entry2.insert(0, 'tháng')
    #entry3 = tk.Entry(child_windown, width=15)
    #entry3.insert(0, 'ngày')
    option = dropdownList(child_windown)
    dropdown = option[0] # Đây là cái list tiền
    entry = option[1] # Đây là loại tiền mình muốn tra cứu
    print("MAY NHAN TIEN GI")
    print(entry)
    butt_search = tk.Button(child_windown, text='Tra cứu', command=lambda: tra_cuu(entry, tree, child_windown))
    butt_thoat = tk.Button(child_windown, text="Thoát", command=lambda: stop_tra_cuu(child_windown))
    #entry1.grid(row=1, column=1)
    #entry2.grid(row=1, column=2)
    #entry3.grid(row=1, column=3)
    dropdownLabel = tk.Label(child_windown, text = "Chọn loại tiền")
    dropdownLabel.grid(row=2, column=1)
    dropdown.grid(row=2, column=2)
    butt_search.grid(row=3, column=2)
    butt_thoat.grid(row=3, column=3)
    #     =====================================
    child_windown.protocol("WM_DELETE_WINDOW", lambda: stop_tra_cuu(child_windown))


def registration(entry1, entry2, entry3, reg_w):
    try:
        client.sendall(bytes("tiep tuc", "utf8"))
        username = entry1.get()
        client.sendall(bytes(username, "utf8"))
        password = entry2.get()
        client.sendall(bytes(password, "utf8"))
        password_agian = entry3.get()
        client.sendall(bytes(password_agian, "utf8"))
        notice = client.recv(1024).decode("utf8")
    except socket.error:
        tkinter.messagebox.showinfo(title="Thông báo", message="Server đã đóng kết nối")
        client.close()
        root.destroy()
        return
    if notice == "Dang ky thanh cong" and password_agian == password:
        tkinter.messagebox.showinfo(title="Thông báo", message="Đăng ký thành công")
        reg_w.destroy()

    else:
        tkinter.messagebox.showerror(title="Lỗi",
                                     message="Tên dăng nhập đã tồn tại hoặc mật khẩu nhập lại không đúng. Hãy thử lại")
        entry1.delete(0, 'end')
        entry2.delete(0, 'end')
        entry3.delete(0, 'end')


def Login(entry1, entry2, log_w):
    try:
        client.sendall(bytes("tiep tuc", "utf8"))
        username = entry1.get()
        client.sendall(bytes(username, "utf8"))
        password = entry2.get()
        client.sendall(bytes(password, "utf8"))
        notice = client.recv(1024).decode("utf8")
    except socket.error:
        tkinter.messagebox.showinfo(title="Thông báo", message="Server đã đóng kết nối")
        client.close()
        root.destroy()
        return
    if notice == "Ban da dang nhap thanh cong":
        tkinter.messagebox.showinfo(title="Thông báo", message="Đăng nhập thành công")
        log_w.destroy()
        # Đăng nhập thành công thì được vào để tra cứu
        tra_cuu_w()
    else:

        tkinter.messagebox.showerror(title="Lỗi",
                                     message="Tên dăng nhập hoặc mật khẩu không đúng. Hãy thử lại")
        entry1.delete(0, 'end')
        entry2.delete(0, 'end')


def on_close(log_w):
    client.sendall(bytes("break", "utf8"))
    log_w.destroy()


# =============Viết GUI cho đăng kí và đăng nhập=============
def registration_w():
    msg = "dang ky"
    try:
        client.sendall(bytes(msg, "utf8"))
    except socket.error:
        tkinter.messagebox.showinfo(title="Thông báo", message="Server đã đóng kết nối")
        client.close()
        root.destroy()
        return
    reg_w = Toplevel(root)
    entry1 = tk.Entry(reg_w, width=35)
    entry1.insert(0, 'Nhập tên đăng nhâp ')
    entry2 = tk.Entry(reg_w, show="*", width=35)
    entry2.insert(0, 'Nhập mật khẩu')
    entry3 = tk.Entry(reg_w, show="*", width=35)
    entry3.insert(0, 'Nhập lại mật khẩu')
    reg_w.geometry("300x300")
    reg_w.title("Đăng ký")
    entry1.grid(row=1, column=1)
    entry2.grid(row=2, column=1)
    entry3.grid(row=3, column=1)
    but_ok = tk.Button(reg_w, text="Đăng ký", command=lambda: registration(entry1, entry2, entry3, reg_w))
    but_ok.grid(row=4, column=2)
    reg_w.protocol("WM_DELETE_WINDOW", lambda: on_close(reg_w))


def Login_w():
    msg = "dang nhap"
    try:
        client.sendall(bytes(msg, "utf8"))
    except socket.error:
        tkinter.messagebox.showinfo(title="Thông báo", message="Server đã đóng kết nối")
        client.close()
        root.destroy()
        return
    log_w = Toplevel(root)
    entry1 = tk.Entry(log_w, width=35)
    entry1.insert(0, 'Nhập tên đăng nhâp ')
    entry2 = tk.Entry(log_w, show="*", width=35)
    entry2.insert(0, 'Nhập mật khẩu')
    log_w.geometry("300x300")
    log_w.title("Đăng nhập")
    entry1.grid(row=1, column=1)
    entry2.grid(row=2, column=1)
    but_ok = tk.Button(log_w, text="Đăng nhập", command=lambda: Login(entry1, entry2, log_w))
    but_ok.grid(row=3, column=2)
    log_w.protocol("WM_DELETE_WINDOW", lambda: on_close(log_w))


def on_exit():
    msg = "exit"
    client.sendall(bytes(msg, "utf8"))
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
myButton_connect = tk.Button(text="Kết nối", command=ConnectToServer)
myButton_connect.grid(row=1, column=2)
myButton_regis = tk.Button(text="Đăng ký", command=registration_w)
myButton_regis.grid(row=2, column=1)
myButton_login = tk.Button(text="Đăng nhập", command=Login_w)
myButton_login.grid(row=3, column=1)
myButton_Exit = tk.Button(text="Thoát", command=on_exit)
myButton_Exit.grid(row=5, column=1)
root.protocol("WM_DELETE_WINDOW", lambda: on_exit())
root.mainloop()
