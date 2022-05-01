import socket
import select

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen()
print("[LISTENING]")

sockets_list = [server_socket]

clients = {}


def receive_message(clients_socket):
    try:
        message_header = clients_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_header = int(message_header.decode('utf-8').strip())
        return {"header": message_header, "data": clients_socket.recv(message_header)}

    except:
        return False


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_sockets in read_sockets:
        if notified_sockets == server_socket:

            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)
            if user is False:
                continue

            sockets_list.append(client_socket)

            clients[client_socket] = user

            usernameData = user['data'].decode('utf-8')

            print(f"[ACCEPTED NEW CONNECTION FROM {client_address[0]}:{client_address[1]} USERNAME:{usernameData}]")

        else:
            message = receive_message(notified_sockets)

            if message is False:
                print(f"[CLOSED CONNECTION FROM {clients[notified_sockets]['data'].decode('utf-8')}]")
                sockets_list.remove(notified_sockets)
                del clients[notified_sockets]
                continue

            user = clients[notified_sockets]
            print(f"[RECEIVED MESSAGE FROM {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}]")

            for client_socks in clients:
                if client_socks != notified_sockets:
                    client_socks.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
