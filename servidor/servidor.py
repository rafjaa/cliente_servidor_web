import os
import socket
import sys

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


print(obtem_ip_externo())

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

    s.bind((ip_servidor, porta))
    s.listen(1)

    print('Aguardando conexão em', ip_servidor, porta)

    con, info_cliente = s.accept()

    print('conexão efetuada por', info_cliente)

    requisicao = con.recv(1024)

    print(requisicao)

    con.send('HTTP/1.1 200 OK\n\n<h1>It works!</h1>'.encode())

