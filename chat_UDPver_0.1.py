# чат - мессенджер
# структура сообщения: msg_nick, dest_nick, msg_data
# структура принятого сообщения: ip, msg_nick, dest_nick, msg_data, mst_time

# interface libs
import tkinter as tk
from tkinter import font
from tkinter import ttk
from tkinter import simpledialog

import socket as sock
import threading as thread
from time import *

import minimumTFTP
from tkinter import filedialog
from tkinter import messagebox
import os

# interface colors
root_color = 'cyan'
sel_color = 'red'

# sizes
btn_width = 14
text_width = 400

list_partners = [('all', '255.255.255.255', -1), ('self', '127.0.0.1', -1), ('hypercube', '192.168.1.150', -1)]
partner_timeout = 3000

# UDP socket for receive messages
HOST_IN = ''
PORT_IN = 4000
BUF_SIZE = 1024
SOCK_ADDR_IN = (HOST_IN, PORT_IN)
uServSock = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
uServSock.bind(SOCK_ADDR_IN)

# очередь для приема сообщений
list_in = []
busy_in = 0
main_tau = 30  # период цикла главной функции`

# UDP socket for transmit messages
HOST_OUT = '127.0.0.1'
PORT_OUT = 4000
# BUF_SIZE = 1024
SOCK_ADDR_OUT = (HOST_OUT, PORT_OUT)
uClientSock = sock.socket(sock.AF_INET, sock.SOCK_DGRAM, sock.IPPROTO_UDP)
uClientSock.setsockopt(sock.SOL_SOCKET, sock.SO_BROADCAST, 1)


# functions

def work_in():
    global list_in
    global busy_in
    # i = 1
    while True:
                                                        # ожидаем данных с сервера
        data, address = uServSock.recvfrom(BUF_SIZE)    # сохраняем данные и адрес отправителя
        local_data = data.decode('cp1251')              # расшифровываем
        local_data = local_data.strip()                 #

        msg_time = str(get_timems())                    # получаем текущее время
        str_data = address[0] + '|' + local_data + '|' + msg_time  # IP + сообщение
        # i = i + 1
        # print(i)
        # аккуратно записываем сообщение в список входящих сообщений
        while busy_in:
            sleep(0.001)
        busy_in = 2
        list_in.append(str_data)
        busy_in = 0

        sleep(0.001)                                    # непонятно почему, но без этого не работает
    uServSock.close()


# функция отправки сообщений адресату
def send_msg(msg, ip):
    print(ip)
    st = msg.encode('cp1251')
    sock_addr = (ip, PORT_OUT)
    uClientSock.sendto(st, sock_addr)


# возвращает время в секундах прошедшее с начала эпохи (int)
def get_timems():
    return int(time() * 1000)

# функция приема файлов по tftp
def work_in_tftp():
    cud_dir = os.getcwd()                           # получить путь к директории работы скрипта
    tftpServer = minimumTFTP.Server(cud_dir)        # настроить сервер на данную директорию
    tftpServer.run()                                # запустить сервер
    while True:
        sleep(0.001)


# create interFace
root = tk.Tk()
dFont = font.Font(family='helvetica', size=12)
style = ttk.Style()

root.configure(background=root_color)
style.configure('.', font=dFont, background=root_color, foreground='black')

ttk.Label(root, text='Simple UDP chat (ver0.1)').grid(row=0, column=0, pady=5)

# left panel. For text messages
panel_left = tk.Frame(root)
panel_left.grid(row=2, column=0, columnspan=6, rowspan=10, pady=10, padx=10)

# left panel. For show messages (main)
panel_msg = tk.Frame(panel_left, width=700)
panel_msg.grid(row=2, column=0)

# text space. For show msgs
text_bx_msg = tk.Text(panel_msg, height=30, wrap=tk.WORD, font=dFont)
text_bx_msg.pack(side='left', fill='both', expand=1)

scroll_bar_msg = tk.Scrollbar(panel_msg)
scroll_bar_msg['command'] = text_bx_msg.yview
text_bx_msg['yscrollcommand'] = scroll_bar_msg.set
scroll_bar_msg.pack(side='right', fill='y')

panel_send = tk.Frame(panel_left)
panel_send.grid(row=3, column=0, pady=5)

tbx_send = tk.Text(panel_send, height=3, wrap=tk.WORD, font=dFont)
tbx_send.pack(side='left', fill='both', expand=1)

scroll_bar_send = tk.Scrollbar(panel_send)
scroll_bar_send['command'] = tbx_send.yview
tbx_send['yscrollcommand'] = scroll_bar_send.set
scroll_bar_send.pack(side='right', fill='y')


# bind on <Enter> pressed       -       обработка нажатия "Enter" при вводе сообщения
def function_tbx_send(event):
    my_nick = var_nick.get()
                                        # не разрешаем отправку сообщения, если нет "регистрации"
    if not my_nick:
        my_nick = simpledialog.askstring('Регистрация', 'Введите ваш ник')
        if not my_nick:                 # если имя так и не ввели - не отправляем сообщение
            return 0
        var_nick.set(my_nick)

    partner_nick = var_partner.get()
    text_send = tbx_send.get(1.0, tk.END).strip()
                                        # собираем "посылку" для отправки адресату
    if len(text_send) > 0:
        send_msg(my_nick + '|' + partner_nick + '|' + text_send, HOST_OUT)
        text_out = '\n( >>> ' + partner_nick + '  ):    ' + text_send
        text_bx_msg.insert(tk.END, text_out)
        tbx_send.delete(1.0, tk.END)


tbx_send.bind("<Return>", function_tbx_send)

# right panel
panel_right = tk.Frame(root, background=root_color)
panel_right.grid(row=0, column=8, rowspan=20)

# nick space
ttk.Label(panel_right, text='Ваше имя:').grid(row=0, column=0, sticky=tk.W, padx=5)
var_nick = tk.StringVar()
var_nick.set('')
edit_nick = ttk.Entry(panel_right, width=btn_width, textvariable=var_nick, font=dFont)
edit_nick.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

# partner nick space
ttk.Label(panel_right, text='Партнер:').grid(row=2, column=0, sticky=tk.W, pady=5)
var_partner = tk.StringVar()
var_partner.set('')
edit_partner = ttk.Entry(panel_right, width=btn_width, textvariable=var_partner, font=dFont)
edit_partner.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

# partners list panel
ttk.Label(panel_right, text='партнеры').grid(row=5, column=0, padx=5, pady=5)
panel_partners = tk.Frame(panel_right)
panel_partners.grid(row=6, column=0, padx=5, pady=5, sticky=tk.N)

listbox_partners = tk.Listbox(panel_partners, width=btn_width, height=16, font=dFont)
listbox_partners.pack(side='left', fill='y')
scrollbar_partners = tk.Scrollbar(panel_partners, orient='vertical')
scrollbar_partners.pack(side='right', fill='y')

scrollbar_partners.config(command=listbox_partners.yview)
listbox_partners.config(yscrollcommand=scrollbar_partners.set)


def func_set_partner(event):
    '''
    binding the double clicking at partner in listbox of partners

    :param event: None
    :return: None
    '''

    global HOST_OUT
    index = listbox_partners.curselection()
    partner = listbox_partners.get(index)
    var_partner.set(partner)
    # print(index, list_partners)
    HOST_OUT = list_partners[index[0]][1]
    # print(HOST_OUT)


listbox_partners.bind("<Double-1>", func_set_partner)


# button for sending a files
def send_file():
    if HOST_OUT == '255.255.255.255':
        msgBox = messagebox.showwarning("Error!!!!!", "U can send file only to a specific partner")
        return

    # select file in dialog window
    file_name = filedialog.askopenfilename(initialdir='.', title='выбыры какой фаел отправить',
                                           filetypes=(('all files', '*.*'), ('txt files', '*.txt')))
    if len(file_name) < 1:
        return
    delim_pos = file_name.rfind('/')    # получаем путь к файлу и имя файла
    path = file_name[:delim_pos]
    file_name = file_name[delim_pos+1:]
    print(path, file_name)

    tftpClient = minimumTFTP.Client(HOST_OUT, path, file_name)
    tftpClient.put()


ttk.Button(panel_right, text='send file', width=btn_width,
           command=send_file).grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)

# when starting soft:
cur_time = get_timems()
list_partners[1] = ("piter", "192.168.1.200", cur_time)
# load partners list
for partner in list_partners:
    listbox_partners.insert(tk.END, partner[0])

# select first partner
listbox_partners.selection_set(0)
partner = listbox_partners.get(0)
var_partner.set(partner)
HOST_OUT = list_partners[0][1]

# create and start threading
tr_in = thread.Thread(target=work_in)
tr_in.daemon = True
tr_in.start()

# get start time
time_stamp = get_timems()

# create and start geting files thread
tr_in_tftp = thread.Thread(target=work_in_tftp)
tr_in_tftp.daemon = True
tr_in_tftp.start()


def main():
    global list_in
    global busy_in
    global time_stamp
    global HOST_OUT

    flag_partnerchange = 0  # сбросить признак изменения партнера
    my_nick = var_nick.get()

    if len(list_in) > 0:
        # carefully get msg from thread
        while busy_in:
            sleep(0.001)
        busy_in = 2
        msg_in = list_in.pop(0)
        busy_in = 0
        # put it in text space
        list_msg = msg_in.split('|')
        msg_ip, msg_nick, dest_nick, msg_data, msg_time = list_msg
        print(msg_ip, msg_nick, dest_nick, msg_data, msg_time)
        msg_time = int(msg_time)

        if msg_nick != my_nick:

            if msg_data != "*":
                text_in = '\n(  ' + msg_nick + '  >>>>   ):    ' + msg_data
                text_bx_msg.insert(tk.END, text_in)

            # find partner in list, using IP
            select_number = -1
            for num, partn in enumerate(list_partners):
                if partn[1] == msg_in and partn[0] == msg_nick:
                    list_partners[num] = (partn[0], partn[1], msg_time)
                    select_number = num
                    break

            # add partner if not find
            if select_number < 0:
                list_partners.append((msg_nick, msg_ip, msg_time))
                flag_partnerchange = 1

    # check time, and delete "old" accounts
    cur_time = get_timems()
    for num in range(len(list_partners) -1, -1, -1):
        if list_partners[num][2] == -1:  # do not delete "all"
            continue
        if cur_time > list_partners[num][2] + 3 * partner_timeout:
            del list_partners[num]
            flag_partnerchange = 1

    # show changes in partner list
    if flag_partnerchange == 1:
        listbox_partners.delete(0, tk.END)
        for partner in list_partners:
            listbox_partners.insert(tk.END, partner[0])

        listbox_partners.selection_set(0)
        partner = listbox_partners.get(0)
        var_partner.set(partner)
        HOST_OUT = '255.255.255.255'

    # send to everyone empty msg
    if cur_time - time_stamp >= partner_timeout:
        time_stamp = cur_time

        if not my_nick:
            my_nick = simpledialog.askstring('Регистрация', 'Введите ваш ник')
            if not my_nick:
                return 0
            var_nick.set(my_nick)

        msg = my_nick + '|all|%*%'
        send_msg(msg, '255.255.255.255')
        sleep(0.005)

    # text_in = '\n(  ' + msg_nick + '  >>>>  ):    ' + msg_data
    # tbx_msg.insert(tk.END, text_in)

    root.after(main_tau, main)


main()

root.mainloop()

uClientSock.close()
