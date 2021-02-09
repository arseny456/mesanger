from socket import *
from functions import *

user_list = []  # таблица юзеров [name, ip]

socket_object = socket(AF_INET, SOCK_STREAM)
socket_object.bind(('', 5400))
socket_object.listen(5)


print("start server")

while True:

    print("ready")
    # Получение и обработка посылки от клиента
    connection, address = socket_object.accept()
    bin_data = connection.recv(1024)
    str_data = bin_data.decode('utf-8')
    ip_addr = address[0]  # ip адрес
    str_answer = ip_addr + '/' + str_data
    print("Я получил сообщение:", str_data, '\n\n',
          'От:', ip_addr)
    connection.sendall(str_answer.encode('utf-8'))
    connection.close()

    # Получение команды из посылки
    list_data = str_data.split('/')
    command = list_data[0]
    try:
        param = list_data[1]
    except:
        param = ''

    # Обработка команд от клиента
    if command == 'registr':
        flag_find = 0
        # проверяем не зарегистрирован ли клиент
        for element in user_list:
            if element[1] == ip_addr:
                flag_find = 1
                break

        # если не зарегистрирован, то регистрируем
        if flag_find == 0:
            user_list.append([param, ip_addr])

            # Подтвердить регистрацию (ответом клиенту)
            str_answer = str_data
            res = send_answer(ip_addr, str_answer)

            # сообщить всем о регистрации игрока
            str_answer = '\n Зарегистрирован игрок: ' + param
            send_to_all(str_answer, user_list)

            print("connection:", res)
            print(user_list)
        else:
            send_answer(ip_addr, "Вы уже зарегистрированны")




