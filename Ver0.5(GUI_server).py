from tkinter import *
from socket import *
import threading
from time import *
from tkinter import simpledialog


name = "Ruslan Sonkin"
list_in = []                        # очередь для принятых сообщений
busy_in = 0                         # признак занятости очереди



def tools_window_f():
    tools_window = Toplevel()
    tools_window.title('tools')


def options_window_f():
    options_window = Toplevel()
    options_window.title('options')


def clear_history():
    text.config(state=NORMAL)
    text.delete(0.0, END)
    text.config(state=DISABLED)


def send_msg(event):
    text.config(state=NORMAL)
    msg = name + ':\n     ' + entry.get() + '\n\n'
    # text.highlight_pattern(name, "red")
    text.insert(END, msg)
    text.config(state=DISABLED)
    entry.delete(0, END)


server_address = ('localhost', 5400)
def send_2_server(event):
    msg = entry.get()
    entry.delete(0, END)
    # bin_msg = msg.encode('utf-8')             !!!!!!!!!!!!!!!
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

    text.config(state=NORMAL)
    text.insert(END, server_msg + '\n\n')
    text.config(state=DISABLED)


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


def display_msg(msg):
    text.config(state=NORMAL)
    text.insert(END, msg + '\n')
    text.yview(END)
    text.config(state=DISABLED)


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

    root.after(20, main)    # after(время_задержки_между_повторениями_в_мс, имя_функции)


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
root = Tk()
root.geometry('275x400+200+200')
root.title('messenger v0.1')

menu = Menu(root)
root.config(menu=menu)

fileMenu = Menu(menu, tearoff=0)
menu.add_cascade(label='File', menu=fileMenu)

fileMenu.add_command(label='Очистка истории сообщений', command=clear_history)
fileMenu.add_command(label='Выход', command=exit)
menu.add_command(label='Tools', command=tools_window_f)
menu.add_command(label='Options', command=options_window_f)

frame_text = Frame(root, )
frame_text.place(x=5, y=5, relwidth=1, relheight=1, width=-5, height=-30)
text = Text(frame_text, state=DISABLED)
text.place(x=0, y=0, relwidth=1, relheight=1, width=-60, height=0)

btn1 = Button(frame_text, text=1, width=7, height=3)
btn1.pack(anchor=NE, pady=5)
btn2 = Button(frame_text, text=2, width=7, height=3)
btn2.pack(anchor=NE, pady=5)
btn3 = Button(frame_text, text=3, width=7, height=3)
btn3.pack(anchor=NE, pady=5)

frame_entry = Frame(root, )
frame_entry.pack(side=BOTTOM, fill=X)

entry = Entry(frame_entry)
entry.pack(side=LEFT, fill=X, expand=1)

btn = Button(frame_entry, text='send', command=lambda: send_2_server(0))
btn.pack(side=RIGHT, padx=5)

entry.bind('<Return>', send_2_server)

btn1.config(state=DISABLED)
btn2.config(state=DISABLED)
btn3.config(state=DISABLED)

main()

root.mainloop()
