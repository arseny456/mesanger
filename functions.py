from socket import *


def send_answer(ip, answer):
    client = socket(AF_INET, SOCK_STREAM)
    try:
        client.connect((ip, 5401))
        client.sendall(answer.encode('utf-8'))
        data = client.recv(1024)
        client_msg = data.decode('utf-8')
        # print(client_msg)
    except:
        client_msg = 'not connected'
        print('not connected')
    finally:
        client.close()

    return client_msg


def send_to_all(msg, user_list):
    '''
    Функция для отправки сообщений всем клиентам подключившимся
    к этому серверу.
    : msg : Отправляемое сообщение (string)
    : user_list : Список подключенных клиентов (list[name, ip])

    Function for sending message to every clients connected
    to this server.
    :param msg: Sending message (string)
    :param user_list: List of connected clients (list[name, ip])
    :return:
    '''
    for element in user_list:
        ip = element[1]
        send_answer(ip, msg)
