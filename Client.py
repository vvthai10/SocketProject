import tkinter as tk
from tkinter import ttk
from tkinter import *
import tkinter.messagebox
import socket
import json
from PIL import  Image,ImageTk
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Use global variable.
index = 0
# =============================FUNCTION============================

#@DESCR: Connect to server.
#@PARAM: None
#@RETURN: None
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

#@DESCR: Stop lookup.
#@PARAM: None
#@RETURN: None
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

#@DESCR: Send request and receive result of server.
#@PARAM: currency, day, month, year, tree
#@RETURN: None
def LookUp(currency, day, month, year, tree ):  
    try:
        isContinue = "continue"
                     
        getCurrency = currency.get()
        getDay = day.get()
        getMonth = month.get()
        getYear = year.get()                        

        if(len(getDay) == 1):
            getDay = "0" + getDay
        if(len(getMonth) == 1):
            getMonth = "0" + getMonth
        
        #================
        client.sendall(bytes(isContinue, "utf8"))
        #================
        inforLoopup_Dict = {"currency": getCurrency, "day": getDay, "month": getMonth, "year": getYear}
        inforLoopup_String = json.dumps(inforLoopup_Dict)
        client.sendall(bytes(inforLoopup_String, "utf8"))
        
    except socket.error:
        tkinter.messagebox.showinfo(title="Notification", message="Server closed connection.")
        client.close()
        root.destroy()
        return
    #Receive result.
    global index
    while True:
        resultServer = client.recv(1024)
        #Change types Bytes to Dict.
        result = json.loads(resultServer.decode('ISO-8859-1'))
        if result == {"id": 0}:
            break
        elif result == {"id": -1}:
            tkinter.messagebox.showinfo("Notification","The time you requested is not available.")
            break
        else:
            index = index + 1
            tree.insert(parent='', index='end', text = "" + str(index), 
                        values=(result['currency'], result['buy_cash'], result['buy_transfer'], result['sell']))

#@DESCR: Send request and receive result of server.
#@PARAM: currency, day, month, year, tree
#@RETURN: None            
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

#@DESCR: Request registration and send information of account.
#@PARAM: UsernameEntry, PassEntry, PassAgianEntry, registerUI.
#@RETURN: None
def Registration(UsernameEntry, PassEntry, PassAgianEntry, registerUI):
    try:
        client.sendall(bytes("continue", "utf8"))
        username = UsernameEntry.get()
        password = PassEntry.get()
        passwordRep = PassAgianEntry.get()
        inforRegis_Dict = {"account": username, "password": password, "password_rep": passwordRep}
        inforURegis_String = json.dumps(inforRegis_Dict)
        client.sendall(bytes(inforURegis_String, "utf8"))
        
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

#@DESCR: Request login and send information of account.
#@PARAM: UsernameEntry, PassEntry, loginUI.
#@RETURN: None
def Login(UsernameEntry, PassEntry, loginUI):
    try:
        client.sendall(bytes("continue", "utf8"))
        username = UsernameEntry.get()
        password = PassEntry.get()
        
        inforUser_Dict = {"account": username, "password": password}
        inforUser_String = json.dumps(inforUser_Dict)
        client.sendall(bytes(inforUser_String, "utf8"))

        noticeServer = client.recv(1024).decode("utf8")
    except socket.error:
        tkinter.messagebox.showinfo(title="Notification", message="Server closed connection.")
        client.close()
        root.destroy()
        return
    if noticeServer == "Login successfully":
        #Get information about date first can lookup.
        dayFirst = client.recv(1024).decode("utf8")
        monthFirst = client.recv(1024).decode("utf8")
        yearFirst = client.recv(1024).decode("utf8")
        print(dayFirst, " + ", monthFirst, " + ", yearFirst)
        tkinter.messagebox.showinfo(title="Notification", message="Login successfully.")
        loginUI.destroy()
        LookUpUI(dayFirst, monthFirst, yearFirst)
    else:
        tkinter.messagebox.showinfo(title="Error", message="Account doesn't exist.")
        UsernameEntry.delete(0, 'end')
        PassEntry.delete(0, 'end')

#@DESCR: Close and send request to server.
#@PARAM: userUI.
#@RETURN: None
def isClose(userUI):
    client.sendall(bytes("break", "utf8"))
    userUI.destroy()

def isExit():
    msgRequest = "exit"
    client.sendall(bytes(msgRequest, "utf8"))
    client.close()
    root.destroy()

# =============Function UI=============
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
    UsernameEntry.insert(0, 'UserName')
    PassEntry = tk.Entry(registerUI, show="*", width=35,font=("Arial", 12),fg='black',border=0,bg='white')
    PassEntry.insert(0, 'Password')
    PassAgianEntry = tk.Entry(registerUI, show="*", width=35,font=("Arial", 12),fg='black',border=0,bg='white')
    PassAgianEntry.insert(0, 'Re-enter password')
    registerUI.geometry("400x300")
    registerUI.title("Sign Up")
    RegisLabel = Label(registerUI,text="Sign up",font=("Arial", 23),fg='#ff4f5a',bg='white')
    RegisLabel.place(x =135 ,y = 20)
    def on_enter(e):
        UsernameEntry.delete(0,'end')    
    def on_leave(e):
        if UsernameEntry.get()=='':   
            UsernameEntry.insert(0,'UserName')
    UsernameEntry.pack()
    UsernameEntry.bind("<FocusIn>", on_enter)
    UsernameEntry.bind("<FocusOut>", on_leave)
    UsernameEntry.place(relx=.5, rely=.3, anchor="center",width=200,height=30)

    def on_enter(e):
        PassEntry.delete(0,'end')    
    def on_leave(e):
        if PassEntry.get()=='':   
            PassEntry.insert(0,'Password')
    PassEntry.pack()
    PassEntry.bind("<FocusIn>", on_enter)
    PassEntry.bind("<FocusOut>", on_leave)
    PassEntry.place(relx=.5, rely=.4, anchor="center",width=200,height=30)

    def on_enter(e):
        PassAgianEntry.delete(0,'end')    
    def on_leave(e):
        if PassAgianEntry.get()=='':   
            PassAgianEntry.insert(0,'Re-enter password')
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
    UsernameEntry.insert(0, 'UserName')
    PassEntry = tk.Entry(loginUI, show="*", width=35,font=("Arial", 12),fg='black',border=0,bg='white')
    PassEntry.insert(0, 'Password')
    loginUI.geometry("400x300")
    loginUI.title("Sign In")
    LoginLabel = Label(loginUI,text="Sign in",font=("Arial", 23),fg='#ff4f5a',bg='white')
    LoginLabel.place(x =145,y = 20)
    def on_enter(e):
        UsernameEntry.delete(0,'end')    
    def on_leave(e):
        if UsernameEntry.get()=='':   
            UsernameEntry.insert(0,'UserName')
    UsernameEntry.pack()
    UsernameEntry.bind("<FocusIn>", on_enter)
    UsernameEntry.bind("<FocusOut>", on_leave)
    UsernameEntry.place(relx=.5, rely=.3, anchor="center",width=200,height=30)
    def on_enter(e):
        PassEntry.delete(0,'end')    
    def on_leave(e):
        if PassEntry.get()=='':   
            PassEntry.insert(0,'Password')
    PassEntry.pack()
    PassEntry.bind("<FocusIn>", on_enter)
    PassEntry.bind("<FocusOut>", on_leave)
    PassEntry.place(relx=.5, rely=.4, anchor="center",width=200,height=30)
    SigninButtom = tk.Button(loginUI, width=15,pady=4 , text="Sign In", bg='#ff4f5a',fg='white',border=0,command=lambda: Login(UsernameEntry, PassEntry, loginUI))
    SigninButtom.pack()
    SigninButtom.place(relx=.5, rely=.6, anchor="center")
    loginUI.protocol("WM_DELETE_WINDOW", lambda: isClose(loginUI))
    Frame(loginUI,width=200,height=1.2,bg='black').place(x=97,y=100)
    Frame(loginUI,width=200,height=1.2,bg='black').place(x=97,y=130)
#@DESCR: Set UI of lookup and print result in screen.
#@PARAM: dayFirst, monthFirst, yearFirst (Use warning user only can lookup after date.)
#@RETURN: None
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
    mainWindown.title("CURRENCY APP")
    mainWindown.geometry("1240x250")
    mainWindown.iconbitmap('dollar.ico')
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

    tree.column('#0', stretch=tk.YES)
    tree.column('#1', stretch=tk.YES)
    tree.column('#2', stretch=tk.YES)
    tree.column('#3', stretch=tk.YES)
    tree.column('#4', stretch=tk.YES)
    tree.grid(row=1, column=4, rowspan=20 ,sticky='nsew')

    #===============================
    inputDay = tk.Entry(mainWindown, width=15)
    
    def on_enter(e):
        inputDay.delete(0,'end')    
    def on_leave(e):
        if inputDay.get()=='':   
            inputDay.insert(0,'Day')

    inputDay.bind("<FocusIn>", on_enter)
    inputDay.bind("<FocusOut>", on_leave)
    inputDay.insert(0, 'Day')

    inputMonth = tk.Entry(mainWindown, width=15)
    def on_enter(e):
        inputMonth.delete(0,'end')    
    def on_leave(e):
        if inputMonth.get()=='':   
            inputMonth.insert(0,'Month')

    inputMonth.bind("<FocusIn>", on_enter)
    inputMonth.bind("<FocusOut>", on_leave)
    inputMonth.insert(0, 'Month')
    
    inputYear = tk.Entry(mainWindown, width=15)
    
    def on_enter(e):
        inputYear.delete(0,'end')    
    def on_leave(e):
        if inputYear.get()=='':   
            inputYear.insert(0,'Year')

    inputYear.bind("<FocusIn>", on_enter)
    inputYear.bind("<FocusOut>", on_leave)
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

#================MAIN=======================

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
            MainEntry.insert(0,'Press IP')
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
RedButtom = tk.PhotoImage(file="redbuttom.png")
RedButtom= RedButtom.subsample(1,1)
ButtomConnect.config(image=RedButtom)
ButtomConnect.place(relx=.7, rely=.3, anchor="center",width=96,height=30)
ButtomRegister = tk.Button(text="Sign Up", command=RegistrationUI,font=("Klavika", 13, 'bold') ,bg="green2",fg='white',border=0)
ButtomRegister.place(relx=.5, rely=.4, anchor="center",width=250,height=30)
ButtomLogin = tk.Button(text="Sign In", command=LoginUI,font=("Klavika",13, 'bold'),bg="blue",fg='white',border=0)
ButtomLogin.place(relx=.5, rely=.5, anchor="center",width=250,height=30)
ButtomExit = tk.Button(text="Exit", command=isExit,bg='#ff4f5a',fg='white',border=0)
ButtomExit.place(relx=.5, rely=.6, anchor="center",width=150,height=30)
root.protocol("WM_DELETE_WINDOW", lambda: isExit())
root.mainloop()
