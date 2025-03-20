import socket
import sys
import threading

#permite a especificação do host ou usa valores padrão
if len(sys.argv) > 2:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
else:
    HOST = '127.0.0.1'
    PORT = 50000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

exit_command_sent = False  # variável para verificar se o comando SAIR foi enviado

#envia mensagens para o servidor
def send_message():
    global exit_command_sent
    while True:
        message = input('Menssagem: ').upper()
        client_socket.send(message.encode())
        if message == 'SAIR':
            exit_command_sent = True
            client_socket.shutdown(socket.SHUT_RDWR)  # Desativa futuras transmissões e recepções
            client_socket.close()  # Fecha o soquete
            break
#recebe as mensagens do servidor        
def receive_message():
    while True:
        try:
            message = client_socket.recv(1024)
        except OSError:
            break
        if not message:
            break
        print(message.decode())

message_translation = {
    'E-ERROR-700': 'Você não está logado.',
    'E-ERROR-702': 'Argumentos inválidos.',
    'E-ERROR-703': 'Nome de usuário já existe.',
    'E-ERROR-704': 'Credenciais inválidas.',
    'E-ERROR-999': 'Comando inválido.',
    'S-PASS-213': 'Usuário registrado com sucesso.',
    'S-PASS-214': 'Login realizado com sucesso.',
    'S-PASS-217': 'Desconectado com sucesso.',
    'M-MESS-215': 'Mensagem enviada com sucesso',
    'M-MESS-216': 'Usuário alvo não está online.'
}

username = ''
#solicita comandos, envia ao servidor e recebe as repostas exibindo-as
while True:
    command = input('Digite um comando: ').upper()
    client_socket.send(command.encode())
    response = client_socket.recv(1024).decode()
    print(f'{response}: {message_translation.get(response, response)}')
    if command.startswith('ENTRAR') and 'S-PASS-214' in response:
        username = command.split(' ')[1]
        threading.Thread(target=receive_message).start()
        send_thread = threading.Thread(target=send_message)
        send_thread.start()
        send_thread.join()
    if exit_command_sent:  # Verifica se o comando SAIR foi enviado
        client_socket.close()  # Fecha o soquete
        break  # Se foi, encerra o loop principal