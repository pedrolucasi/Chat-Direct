import socket
import threading

# HOST vazio para aceitar conexões em todas as interfaces 
HOST = '0.0.0.0'
PORT = 50000

# variáveis globais para manter o estado dos usuários ativos e outra para garantir a consistência dos dados em multi-threaded
active_users = {}
lock_active_users = threading.Lock()

# processamento da comunicação lidando com mensagens, comandos e estado do usuário
def handle_client(client_socket, address):
    username = ''
    try:
        while True:
            message = client_socket.recv(1024)
            if not message:
                break
            message = message.decode().strip()
            print(f"Mensagem recebida de {username}: {message}")  
            response, username = process_message(message, client_socket, address, username)
            if response is not None:
                try:
                    client_socket.send(response.encode())
                except OSError as e:
                    print(f"Erro ao enviar resposta: {e}")
                    break
            if response == 'S-PASS-217':
                break  # encerra o loop após o comando SAIR
    except OSError as e:
        print(f"Erro de socket: {e}")
    finally:
        print("Cliente desconectado")
        client_socket.close()

#porcessamento das mensagens recebidas vinda do cliente executando os comandos
def process_message(message, client_socket, address, username):
    parts = message.split(' ')
    command = parts[0]

    if command == 'NOVO':
        with lock_active_users:
            if len(parts) != 3:
                return ['E-ERROR-702', '']
            _, username, password = parts
            if username in active_users:
                return ['E-ERROR-703', '']
            active_users[username] = {'password': password, 'socket': client_socket}
            return ['S-PASS-213', username]
        
    elif command == 'ENTRAR':
        with lock_active_users:
            if len(parts) != 3:
                return ['E-ERROR-702', '']
            _, username, password = parts
            if username not in active_users or active_users[username]['password'] != password:
                return ['E-ERROR-704', '']
            return ['S-PASS-214', username]
    
    elif command == 'MESS':
        with lock_active_users:
            if len(parts) < 3:
                return ['E-ERROR-702', '']
            _, target, *msg_parts = parts
            msg = ' '.join(msg_parts)
            if target in active_users:
                active_users[target]['socket'].send(f'{username}: {msg}'.encode())
                return ['M-MESS-215', username]
            else:
                return ['M-MESS-216', username]
        
    elif command == 'LISTA':
        return [', '.join(active_users.keys()), username]
    
    elif command == 'SAIR':
        active_users.pop(username)
        client_socket.shutdown(socket.SHUT_RDWR)  # Desativa futuras transmissões e recepções
        client_socket.close()  # Fecha o soquete
        return [None, '']

    return ['E-ERROR-999', '']

#configuração de inicialização do servidor, aceitando conexões e criando as threads para tratar cada cliente
def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print('Servidor iniciado.')
    while True:
        client_socket, address = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, address)).start()
        print(f'Cliente {address} conectado!')
    server_socket.close()

if __name__ == '__main__':
    main()