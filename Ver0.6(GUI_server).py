from tkinter import *
from socket import *
import threading
from time import *
from tkinter import simpledialog

name = "Ruslan Sonkin"
list_in = []  # очередь для принятых сообщений
busy_in = 0  # признак занятости очереди


server_address = ('localhost', 5400)


# Аккуратно записать сообщение в очередь
def put_msg(msg: str):
    global list_in
    global busy_in
    while busy_in:
        sleep(0.001)
    busy_in = 1
    list_in.append(msg)
    busy_in = 0


# Функция приема сообщений (один раз за пакет)
def work_in():
    global list_in
    global busy_in

    local_server_address = ('', 5401)
    local_socket = socket(AF_INET, SOCK_STREAM)
    local_socket.bind(local_server_address)
    local_socket.listen(5)

    while True:
        # Ждать и получить сообщение от сервера...
        print('ready')
        connection, address = local_socket.accept()
        print('connection. Address:', address)
        bin_data = connection.recv(1024)
        str_data = bin_data.decode('utf-8')
        print(str_data, "from work_in")
        connection.close()

        # ...записать его в очередь сообщений
        put_msg(str_data)

        # задержка потока
        sleep(0.001)


# Настройка потока приема сообщений
threading_in = threading.Thread(target=work_in)
threading_in.daemon = True
threading_in.start()


# Главная функция запускаемая в цикле
def main():
    global list_in
    global busy_in

    if len(list_in) > 0:
        while busy_in:
            sleep(0.001)
        busy_in = 1
        str_in = list_in.pop()
        busy_in = 0

        # print(str_in, 'from main func')
        display_msg(str_in)

    root.after(20, main)  # after(время_задержки_между_повторениями_в_мс, имя_функции)


def registr():
    # global server_address

    def registr_f():
        serv_addr = reg_name_entry.get()

    registr_window = Toplevel(root)
    registr_window.title('Окно регистрации')
    reg_server_address_entry = Entry(registr_window)
    reg_server_address_entry.pack()
    reg_name_entry = Entry(registr_window)
    reg_name_entry.pack()
    reg_btn = Button(text='Зарегистрироваться!', command=registr_f)
    reg_btn.pack()


# Создание интерфейса
class messenger:
    def __init__(self, root):
        self.root = root
        self.root.geometry('275x400+200+200')
        self.root.title('messenger v0.6')

        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)

        self.fileMenu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='File', menu=self.fileMenu)

        self.fileMenu.add_command(label='Очистка истории сообщений', command=self.clear_history)
        self.fileMenu.add_command(label='Выход', command=exit)
        self.menu.add_command(label='Tools', command=self.tools_window_f)
        self.menu.add_command(label='Options', command=self.options_window_f)

        self.frame_text = Frame(root,)
        self.frame_text.place(x=5, y=5, relwidth=1, relheight=1, width=-5, height=-30)
        self.text = Text(self.frame_text, state=DISABLED)
        self.text.place(x=0, y=0, relwidth=1, relheight=1, width=-60, height=0)

        self.btn1 = Button(self.frame_text, text=1, width=7, height=3)
        self.btn1.pack(anchor=NE, pady=5)
        self.btn2 = Button(self.frame_text, text=2, width=7, height=3)
        self.btn2.pack(anchor=NE, pady=5)
        self.btn3 = Button(self.frame_text, text=3, width=7, height=3)
        self.btn3.pack(anchor=NE, pady=5)

        self.frame_entry = Frame(root,)
        self.frame_entry.pack(side=BOTTOM, fill=X)

        self.entry = Entry(self.frame_entry)
        self.entry.pack(side=LEFT, fill=X, expand=1)

        self.send_btn = Button(self.frame_entry, text='send', command=lambda: self.send_2_server(0))
        self.send_btn.pack(side=RIGHT, padx=5)

        self.entry.bind('<Return>', self.send_2_server)
        self.btn1.config(state=DISABLED)
        self.btn2.config(state=DISABLED)
        self.btn3.config(state=DISABLED)

        self.nick_name = ''

    def nick_name_f(self):
        dialog = simpledialog.askstring("Регистрация", "Введите имя")
        if dialog:
            self.nick_name = dialog

    def options_window_f(self):
        self.options_window = Toplevel()
        self.options_window.title('options')

    def tools_window_f(self):
        self.tools_window = Toplevel()
        self.tools_window.title('tools')

    def clear_history(self):
        self.text.config(state=NORMAL)
        self.text.delete(0.0, END)
        self.text.config(state=DISABLED)

    def send_2_server(self, event):
        if not self.nick_name:
            self.nick_name_f()
            if not self.nick_name:
                return 0
        msg = self.entry.get()
        self.entry.delete(0, END)
        # bin_msg = msg.encode('utf-8')             !!!!!!!!!!!!!!!
        if msg:
            bin_msg = bytes(msg, 'UTF-8')

            server_msg = ''

            client = socket(AF_INET, SOCK_STREAM)
            try:
                client.connect(server_address)
                client.sendall(bin_msg)
                data = client.recv(1024)
                server_msg = data.decode('utf-8')
                print(server_msg)
            except:
                server_msg = 'not connected'
                print('not connected')
            finally:
                client.close()

            self.text.config(state=NORMAL)
            self.text.insert(END, server_msg + '\n\n')
            self.text.config(state=DISABLED)

    def display_msg(self, msg):
        self.text.config(state=NORMAL)
        self.text.insert(END, msg + '\n')
        self.text.yview(END)
        self.text.config(state=DISABLED)

    def send_msg(self, event):
        self.text.config(state=NORMAL)
        self.msg = name + ':\n     ' + self.entry.get() + '\n\n'
        # text.highlight_pattern(name, "red")
        self.text.insert(END, self.msg)
        self.text.config(state=DISABLED)
        self.entry.delete(0, END)


# root = Tk()
# root.geometry('275x400+200+200')
# root.title('messenger v0.1')
#
# menu = Menu(root)
# root.config(menu=menu)
#
# fileMenu = Menu(menu, tearoff=0)
# menu.add_cascade(label='File', menu=fileMenu)
#
# fileMenu.add_command(label='Очистка истории сообщений', command=clear_history)
# fileMenu.add_command(label='Выход', command=exit)
# menu.add_command(label='Tools', command=tools_window_f)
# menu.add_command(label='Options', command=options_window_f)
#
# frame_text = Frame(root, )
# frame_text.place(x=5, y=5, relwidth=1, relheight=1, width=-5, height=-30)
# text = Text(frame_text, state=DISABLED)
# text.place(x=0, y=0, relwidth=1, relheight=1, width=-60, height=0)
#
# btn1 = Button(frame_text, text=1, width=7, height=3)
# btn1.pack(anchor=NE, pady=5)
# btn2 = Button(frame_text, text=2, width=7, height=3)
# btn2.pack(anchor=NE, pady=5)
# btn3 = Button(frame_text, text=3, width=7, height=3)
# btn3.pack(anchor=NE, pady=5)
#
# frame_entry = Frame(root, )
# frame_entry.pack(side=BOTTOM, fill=X)
#
# entry = Entry(frame_entry)
# entry.pack(side=LEFT, fill=X, expand=1)
#
# btn = Button(frame_entry, text='send', command=lambda: send_2_server(0))
# btn.pack(side=RIGHT, padx=5)
#
# entry.bind('<Return>', send_2_server)
#
# btn1.config(state=DISABLED)
# btn2.config(state=DISABLED)
# btn3.config(state=DISABLED)

root = Tk()
window = messenger(root)

main()

window.nick_name_f()

window.root.mainloop()

