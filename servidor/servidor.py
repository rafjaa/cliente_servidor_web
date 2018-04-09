import os
import socket
import sys
import time

from threading import Thread

import magic


# Caso False, escuta em localhost
USAR_IP_EXTERNO = False

HTML_LISTAGEM = '''
    <!doctype html>
    <html>
        <head>
            <meta charset="utf-8">
            <title>{0}</title>
            <style type="text/css">
                *{{
                    margin: 0;
                    padding: 0;
                    font-family: sans-serif;
                }}
            </style>
        </head>
        <body>
            <h1>{0}</h1>
            <p>
                {2}
            </p>
            {1}
        </body>
    </html>
'''

HTML_NOT_FOUND = '''
    <!doctype html>
    <html>
        <head>
            <meta charset="utf-8">
            <title>404 Not Found</title>
            <style type="text/css">
                *{{
                    margin: 0;
                    padding: 0;
                    font-family: sans-serif;
                }}
            </style>
        </head>
        <body>
            <h1>Recurso não encontrado (404 Not Found)</h1>
            <p>Clique <a href="/">aqui</a> para acessar a listagem de arquivos da raiz</p>
        </body>
    </html>
'''

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

    try:
        metodo_http, recurso, versao_http = inicio_requisicao.split(' ')
    except ValueError:
        metodo_http = 'GET'
        recurso = '/'
        versao_http = 'HTTP/1.1'

    print(metodo_http, recurso, versao_http)

    # Evita o uso de .. para voltar diretórios
    recurso = recurso.replace('..', ' ').replace('//', '/')

    # 400 Bad Request
    # 500 Internal Server Error
    codigo_resposta = '200'
    txt_resposta = 'OK'
    conteudo_resposta = '<h1>It works!</h1>'
    content_type = 'text/html'


    # Checa se o recurso existe e se é um arquivo ou diretório
    caminho_recurso = (diretorio + recurso).replace('//', '/')
    print('Analisando:', caminho_recurso)

    if os.path.isfile(caminho_recurso):
        print('Arquivo')

        # Descobre o MIME type do arquivo
        mime = magic.Magic(mime=True)
        content_type = mime.from_file(caminho_recurso)

        # Lê o conteúdo do arquivo
        conteudo_resposta = open(caminho_recurso, 'rb').read()

    
    elif os.path.isdir(caminho_recurso):
        print('Diretório')

        listagem = ''
        for i in os.listdir(caminho_recurso):
            
            data_modificacao = time.ctime(os.path.getmtime(caminho_recurso.rstrip('/') + '/' + i))
            tamanho_bytes = str(os.path.getsize(caminho_recurso.rstrip('/') + '/' + i))

            listagem += '<div class="item_listagem">'
            listagem += '<a href="' + recurso.rstrip('/') + '/' + i + '">' + i + '</a>'
            listagem += '<span>' + tamanho_bytes + '</span>'
            listagem += '<span>' + data_modificacao + '</span>'
            listagem += '</div>'

        conteudo_resposta = HTML_LISTAGEM.format(
            'Listagem de diretório de ' + caminho_recurso, 
            listagem,
            '<a href="../">..</a>' if caminho_recurso.rstrip('/') != diretorio.rstrip('/') else ''
        )
    
    else:
        print('Não existe')
        codigo_resposta = '404'
        txt_resposta = 'Not Found'
        conteudo_resposta = HTML_NOT_FOUND


    # Cabeçalho de resposta HTTP
    cabecalho_resp = 'HTTP/1.1 {0} {1}\nContent-Type: {2}\n\n'.format(
        codigo_resposta, 
        txt_resposta,
        content_type
    )

    # Envia o cabeçalho para o cliente
    con.send(cabecalho_resp.encode())

    # Envia o conteúdo para o cliente
    TAM_BUFFER = 1024

    # Codifica o conteúdo caso o mesmo não esteja em formato binário
    if isinstance(conteudo_resposta, str):
        conteudo_resposta = conteudo_resposta.encode()

    for i in range(0, len(conteudo_resposta), TAM_BUFFER):
        try:
            con.send(conteudo_resposta[i:i + TAM_BUFFER])
        except BrokenPipeError:
            pass

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


    while True:
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
    
        s.listen(1)

        print('Aguardando conexão em', ip_servidor, porta)

        con, info_cliente = s.accept()

        print('conexão efetuada por', info_cliente)

        # Processa a requisição em uma thread paralela
        Thread(target=processa_requisicao, args=(con, )).start()