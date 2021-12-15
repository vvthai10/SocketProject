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
    HOST = MainEntry.get()
    PORT = 65432
    ImageScr = True
    try:
        client.connect((HOST, PORT))
    except Exception as e:
        tkinter.messagebox.showerror(title="Error", message="Unable to connect to server.")
        ImageScr = False
    if ImageScr:
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


def LookUp(currency, day, month, year, tree ):   #, child_windown
    try:
        isContinue = "continue"
                     
        getCurrency = currency.get()  #lấy thông tin loại tiền muốn tra cứu
        getDay = day.get()
        getMonth = month.get()
        getYear = year.get()                        

        if(len(getDay) == 1):
            getDay = "0" + getDay
        if(len(getMonth) == 1):
            getMonth = "0" + getMonth
        
        print(getCurrency)
        print(getDay)
        print(getMonth)
        print(getYear)
        #================
        print("Gui continue")
        client.sendall(bytes(isContinue, "utf8"))
        #================
        inforLoopup_Dict = {"currency": getCurrency, "day": getDay, "month": getMonth, "year": getYear}
        inforLoopup_String = json.dumps(inforLoopup_Dict)
        print("Gui thong tin tra cuu")
        client.sendall(bytes(inforLoopup_String, "utf8"))
        '''
        print("GỬI DÒNG 3")
        client.sendall(bytes(getDay, "utf8"))
        print("GỬI DÒNG 4")
        client.sendall(bytes(getMonth, "utf8"))
        print("GỬI DÒNG 5")
        client.sendall(bytes(getYear, "utf8"))
        '''
    except socket.error:
        tkinter.messagebox.showinfo(title="Notification", message="Server closed connection.")
        client.close()
        root.destroy()
        return
    #Thực hiện nhiều lần yêu cầu của người dùng.
    i = 1
    while True:
        #3072
        #1024
        resultServer = client.recv(1024)
        #Chuyển kết quả từ bytes sang kiểu dict
        
        result = json.loads(resultServer.decode('ISO-8859-1'))
        if result == {"id": 0}:
            break
        elif result == {"id": -1}:
            #HÌNH NHƯ MÌNH KHÔNG CẦN THÊM CÁI NÀY.
            tkinter.messagebox.showinfo("Thông báo","Thời gian bạn yêu cầu không có, hãy đảm bảo thời gian chính xác.")
            break
        else:
            tree.insert(parent='', index='end', text = "" + str(i), 
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


def LookUpUI(dayFirst, monthFirst, yearFirst):
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
    mainWindown.geometry("1240x250")
    columns = ('Money', 'buy_cash', 'buy_transfer', 'sell')
    tree = ttk.Treeview(mainWindown, columns=columns)
    vsb = ttk.Scrollbar(mainWindown, orient = "vertical", command = tree.yview)
    vsb.place(x = 1220, y = 30, height = 165)
    tree.configure(yscrollcommand = vsb.set)

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
    tree.grid(row=1, column=4, rowspan=20 ,sticky='nsew')

    #===============================
    inputDay = tk.Entry(mainWindown, width=15)
    inputDay.insert(0, 'Day')
    inputMonth = tk.Entry(mainWindown, width=15)
    inputMonth.insert(0, 'Month')
    inputYear = tk.Entry(mainWindown, width=15)
    inputYear.insert(0, 'Year')
    #=========================================
    inputDay.grid(row=1, column=1)
    inputMonth.grid(row=2, column=1)
    inputYear.grid(row=3, column=1)
    #==================================================
    #label = tk.Label(app, bg="white", pady=5, font=(None, 1), height=20, width=720)
    msgWarning = tk.Label(mainWindown, bg = "red", text = "You can only look up the date:" 
                                                + str(dayFirst) + "/" 
                                                + str(monthFirst) + "/"  
                                                + str(yearFirst))
    msgWarning.grid(row = 20, column = 1, columnspan=3, padx=10) 

    option = dropDownList(mainWindown)
    dropdown = option[0] # Đây là cái list tiền
    inputCurrency = option[1] # Đây là loại tiền mình muốn tra cứu
    buttonSearch = tk.Button(mainWindown, text='Lookup', command=lambda: LookUp(inputCurrency, inputDay, inputMonth, inputYear, tree)) #, mainWindown
    buttonExit = tk.Button(mainWindown, text="Exit", command=lambda: stopLookup(mainWindown))
    
    dropdownLabel = tk.Label(mainWindown, text = "Choose Currency")
    dropdownLabel.grid(row=1, column=3, padx=10)
    dropdown.grid(row=2, column=3, padx=10)
    buttonSearch.grid(row=12, column=1, ipadx=6, ipady=4)
    buttonExit.grid(row=12, column=3, ipadx=6, ipady=4)
    #     =====================================
    mainWindown.protocol("WM_DELETE_WINDOW", lambda: stopLookup(mainWindown))


def Registration(UsernameEntry, PassEntry, PassAgianEntry, registerUI):
    try:
        client.sendall(bytes("continue", "utf8"))
        username = UsernameEntry.get()
        password = PassEntry.get()
        passwordRep = PassAgianEntry.get()
        inforRegis_Dict = {"account": username, "password": password, "password_rep": passwordRep}
        inforURegis_String = json.dumps(inforRegis_Dict)
        client.sendall(bytes(inforURegis_String, "utf8"))
        '''
        client.sendall(bytes(username, "utf8"))
        client.sendall(bytes(password, "utf8"))
        client.sendall(bytes(passwordRep, "utf8"))
        '''

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
        UsernameEntry.delete(0, 'end')
        PassEntry.delete(0, 'end')
        PassAgianEntry.delete(0, 'end')


def Login(UsernameEntry, PassEntry, loginUI):
    try:
        client.sendall(bytes("continue", "utf8"))
        username = UsernameEntry.get()
        password = PassEntry.get()
        
        inforUser_Dict = {"account": username, "password": password}
        inforUser_String = json.dumps(inforUser_Dict)
        print(inforUser_Dict)
        print(type(inforUser_Dict))
        client.sendall(bytes(inforUser_String, "utf8"))
        #client.sendall(bytes(password, "utf8"))

        noticeServer = client.recv(1024).decode("utf8")
        print("Gui thong tin ve")
    except socket.error:
        tkinter.messagebox.showinfo(title="Notification", message="Server closed connection.")
        client.close()
        root.destroy()
        return
    if noticeServer == "Login successfully":
        #KHI ĐĂNG NHẬP THÀNH CÔNG< NHẬN THÔNG TIN XEM GIỚI HẠN NGÀY TRA CỨU.
        dayFirst = client.recv(1024).decode("utf8")
        monthFirst = client.recv(1024).decode("utf8")
        yearFirst = client.recv(1024).decode("utf8")
        print(dayFirst, " + ", monthFirst, " + ", yearFirst)
        tkinter.messagebox.showinfo(title="Notification", message="Login successfully.")
        loginUI.destroy()
        # Đăng nhập thành công thì được vào để tra cứu
        LookUpUI(dayFirst, monthFirst, yearFirst)
    else:
        tkinter.messagebox.showinfo(title="Error", message="Account doesn't exist.")
        UsernameEntry.delete(0, 'end')
        PassEntry.delete(0, 'end')


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
    registerUI.iconbitmap('dollar.ico')
    registerUI.config(bg='white')
    UsernameEntry = tk.Entry(registerUI, width=35,font=("Arial", 12),fg='black',border=0,bg='white')
    UsernameEntry.insert(0, 'Nhập tên đăng nhâp ')
    PassEntry = tk.Entry(registerUI, show="*", width=35,font=("Arial", 12),fg='black',border=0,bg='white')
    PassEntry.insert(0, 'Nhập mật khẩu')
    PassAgianEntry = tk.Entry(registerUI, show="*", width=35,font=("Arial", 12),fg='black',border=0,bg='white')
    PassAgianEntry.insert(0, 'Nhập lại mật khẩu')
    registerUI.geometry("400x300")
    registerUI.title("Đăng ký")
    RegisLabel = Label(registerUI,text="Sign up",font=("Arial", 23),fg='#ff4f5a',bg='white')
    RegisLabel.place(x =135 ,y = 20)
    def on_enter(e):
        UsernameEntry.delete(0,'end')    
    def on_leave(e):
        if UsernameEntry.get()=='':   
            UsernameEntry.insert(0,'Nhập tên đăng nhập')
    UsernameEntry.pack()
    UsernameEntry.bind("<FocusIn>", on_enter)
    UsernameEntry.bind("<FocusOut>", on_leave)
    UsernameEntry.place(relx=.5, rely=.3, anchor="center",width=200,height=30)

    def on_enter(e):
        PassEntry.delete(0,'end')    
    def on_leave(e):
        if PassEntry.get()=='':   
            PassEntry.insert(0,'Nhập mật khẩu')
    PassEntry.pack()
    PassEntry.bind("<FocusIn>", on_enter)
    PassEntry.bind("<FocusOut>", on_leave)
    PassEntry.place(relx=.5, rely=.4, anchor="center",width=200,height=30)

    def on_enter(e):
        PassAgianEntry.delete(0,'end')    
    def on_leave(e):
        if PassAgianEntry.get()=='':   
            PassAgianEntry.insert(0,'Nhập lại mật khẩu')
    PassAgianEntry.pack()
    PassAgianEntry.bind("<FocusIn>", on_enter)
    PassAgianEntry.bind("<FocusOut>", on_leave)
    PassAgianEntry.place(relx=.5, rely=.5, anchor="center",width=200,height=30)

    SignupButtom = tk.Button(registerUI, width=15,pady=4,text="Đăng ký",bg='#ff4f5a',fg='white',border=0, command=lambda: Registration(UsernameEntry, PassEntry, PassAgianEntry, registerUI))
    SignupButtom.pack()
    SignupButtom.place(relx=.5 ,rely=.7, anchor="center")
    registerUI.protocol("WM_DELETE_WINDOW", lambda: isClose(registerUI))
    Frame(registerUI,width=200,height=1.2,bg='black').place(x=97,y=100)
    Frame(registerUI,width=200,height=1.2,bg='black').place(x=97,y=130)
    Frame(registerUI,width=200,height=1.2,bg='black').place(x=97,y=160)


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
    loginUI.iconbitmap('dollar.ico')
    loginUI.config(bg='white')
    UsernameEntry = tk.Entry(loginUI, width=35,font=("Arial", 12),fg='black',border=0,bg='white' )
    UsernameEntry.insert(0, 'Nhập tên đăng nhâp ')
    PassEntry = tk.Entry(loginUI, show="*", width=35,font=("Arial", 12),fg='black',border=0,bg='white')
    PassEntry.insert(0, 'Nhập mật khẩu')
    loginUI.geometry("400x300")
    loginUI.title("Đăng nhập")
    LoginLabel = Label(loginUI,text="Sign in",font=("Arial", 23),fg='#ff4f5a',bg='white')
    LoginLabel.place(x =145,y = 20)
    def on_enter(e):
        UsernameEntry.delete(0,'end')    
    def on_leave(e):
        if UsernameEntry.get()=='':   
            UsernameEntry.insert(0,'Nhập tên đăng nhập')
    UsernameEntry.pack()
    UsernameEntry.bind("<FocusIn>", on_enter)
    UsernameEntry.bind("<FocusOut>", on_leave)
    UsernameEntry.place(relx=.5, rely=.3, anchor="center",width=200,height=30)
    def on_enter(e):
        PassEntry.delete(0,'end')    
    def on_leave(e):
        if PassEntry.get()=='':   
            PassEntry.insert(0,'Nhập tên đăng nhập')
    PassEntry.pack()
    PassEntry.bind("<FocusIn>", on_enter)
    PassEntry.bind("<FocusOut>", on_leave)
    PassEntry.place(relx=.5, rely=.4, anchor="center",width=200,height=30)
    SigninButtom = tk.Button(loginUI, width=15,pady=4 , text="Đăng nhập", bg='#ff4f5a',fg='white',border=0,command=lambda: Login(UsernameEntry, PassEntry, loginUI))
    SigninButtom.pack()
    SigninButtom.place(relx=.5, rely=.6, anchor="center")
    loginUI.protocol("WM_DELETE_WINDOW", lambda: isClose(loginUI))
    Frame(loginUI,width=200,height=1.2,bg='black').place(x=97,y=100)
    Frame(loginUI,width=200,height=1.2,bg='black').place(x=97,y=130)


def isExit():
    msgRequest = "exit"
    client.sendall(bytes(msgRequest, "utf8"))
    client.close()
    root.destroy()


# -------------main-----------------

root = tk.Tk()
root.geometry("800x570")
root.title("App")
MainImage=Image.open("background.PNG")
ImageScr=ImageTk.PhotoImage(MainImage)
root.iconbitmap('dollar.ico')
MainLabel = tkinter.Label(image=ImageScr)
MainLabel.image = ImageScr
MainLabel.place(x=1,y=1)
def on_enter(e):
        MainEntry.delete(0,'end')    
def on_leave(e):
        if MainEntry.get()=='':   
            MainEntry.insert(0,'Nhập tên đăng nhập')
MainEntry = tk.Entry(font=("Arial", 12),fg='black',bg='white')
MainEntry.place(relx=.5, rely=.3, anchor="center",width=300,height=30)
MainEntry.bind("<FocusIn>", on_enter)
MainEntry.bind("<FocusOut>", on_leave)
MainEntry.insert(0,'Press IP')
ButtomConnect = tk.Button(text="Conect", command=connectToServer,
    bd=0,
    relief="groove",
    compound=tk.CENTER,
    bg="black",
    fg="white",
    activeforeground="black",
    activebackground="white",
    font="arial 13",
    pady=10,
)
RedButtom = tk.PhotoImage(file="red.png")
RedButtom= RedButtom.subsample(1,1)
ButtomConnect.config(image=RedButtom)
ButtomConnect.place(relx=.7, rely=.3, anchor="center",width=96,height=30)
ButtomRegister = tk.Button(text="Đăng ký", command=RegistrationUI,font=("Klavika", 13, 'bold') ,bg="green2",fg='white',border=0)
ButtomRegister.place(relx=.5, rely=.4, anchor="center",width=250,height=30)
ButtomLogin = tk.Button(text="Đăng nhập", command=LoginUI,font=("Klavika",13, 'bold'),bg="blue",fg='white',border=0)
ButtomLogin.place(relx=.5, rely=.5, anchor="center",width=250,height=30)
ButtomExit = tk.Button(text="Thoát", command=isExit,bg='#ff4f5a',fg='white',border=0)
ButtomExit.place(relx=.5, rely=.6, anchor="center",width=150,height=30)
root.protocol("WM_DELETE_WINDOW", lambda: isExit())
root.mainloop()
