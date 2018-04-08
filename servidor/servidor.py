import os
import socket
import sys
from threading import Thread

# Caso False, escuta em localhost
USAR_IP_EXTERNO = False

def obtem_ip_externo():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip_externo = s.getsockname()[0]
        s.close()

        return ip_externo
    except:
        return 'localhost'


ip_servidor = 'localhost'
if USAR_IP_EXTERNO:
    ip_servidor = obtem_ip_externo()


def processa_requisicao(con):
    requisicao = con.recv(2048).decode()

    # Processa os campos da requisição HTTP
    inicio_requisicao = False
    campos_requisicao = {}

    for l in requisicao.split('\n'):
        if not inicio_requisicao:
            inicio_requisicao = l
            continue

        campo = l.strip('\r').split(':')[0]
        valor = ':'.join(l.strip('\r').split(':')[1:]).strip()

        campos_requisicao[campo] = valor

    print(campos_requisicao)

    metodo_http, recurso, versao_http = inicio_requisicao.split(' ')
    print(metodo_http, recurso, versao_http)


    # Envia a resposta para o cliente
    con.send('HTTP/1.1 200 OK\n\n<h1>It works!</h1>'.encode())

    # Fecha a conexão
    con.close()



if __name__ == '__main__':

    # Obtém a porta e o diretório por linha de comando
    try:
        porta = int(sys.argv[1])
        diretorio = sys.argv[2]

        # Checa se é um diretório válido
        if not os.path.isdir(diretorio):
            print('Forneça um diretório válido.')
            sys.exit()
    except:
        print('Modo de uso: python3 servidor.py porta diretorio')
        sys.exit()


    print(porta, diretorio)


    # Instancia o socket TCP IPv4
    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    # Permite que a porta do servido seja utilizada sucessivas vezes, 
    # sem necessitar de aguardar um tempo de espera
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        s.bind((ip_servidor, porta))
    except PermissionError:
        print('Você não possui permissão para utilizar essa porta.')
        sys.exit()

    while True:
        s.listen(1)

        print('Aguardando conexão em', ip_servidor, porta)

        con, info_cliente = s.accept()

        print('conexão efetuada por', info_cliente)

        # Processa a requisição em uma thread paralela
        Thread(target=processa_requisicao, args=(con, )).start()