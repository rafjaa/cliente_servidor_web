import datetime
import os
import socket
import sys
import time

from threading import Thread

import magic


# Caso False, escuta em localhost
USAR_IP_EXTERNO = False

ARQUIVO_LOG = 'log_servidor.txt'

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

                body{{
                    background-color: #eceef1;
                }}

                main{{
                    display: block;
                    margin: 15px;
                    padding: 50px 100px;
                    background-color: #fff;
                    height: calc(100vh - 150px);
                }}

                h1{{
                    margin-bottom: 50px;
                }}

                a, span{{
                    display: inline-block;
                }}

                a{{
                    width: 30%;
                    padding-left: 15px;
                }}

                a{{
                    font-weight: bold
                }}

                .tam_bytes{{
                    width: 15%;
                    padding: 20px 50px;
                    text-align: center;
                }}

                .mod_date{{
                    width: 30%;
                    padding: 20px 50px;
                    text-align: center;
                }}

                .item_listagem{{
                    border-bottom: solid 1px #eee;
                }}

                .titulo_listagem{{
                    font-weight: bold;
                    text-transform: uppercase;
                    font-size: 13px;
                }}

                .t{{
                    text-align: left;
                    width: 30%;
                    padding-left: 15px;
                }}

                .voltar{{
                    font-size: 20px;
                }}
            </style>
        </head>
        <body>
            <main>
                <h1>{0}</h1>
                <p class="voltar">
                    {2}
                </p>
                <div class="titulo_listagem">
                    <span class="t">Nome</span>
                    <span class="tam_bytes">Tamanho (bytes)</span>
                    <span class="mod_date">Última modificação</span>
                </div>
                {1}
            </main>
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
                *{
                    margin: 0;
                    padding: 0;
                    font-family: sans-serif;
                }

                body{
                    background-color: #eceef1;
                }

                main{
                    display: block;
                    margin: 15px;
                    padding: 50px 100px;
                    background-color: #fff;
                    height: calc(100vh - 150px);
                }

                h1{
                    margin-bottom: 50px;
                }

                a{
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <main>
                <h1>Recurso não encontrado (404 Not Found)</h1>
                <p>Clique <a href="/">aqui</a> para acessar a listagem de arquivos da raiz.</p>
            </main>
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


    try:
        metodo_http, recurso, versao_http = inicio_requisicao.split(' ')
    except ValueError:
        metodo_http = 'GET'
        recurso = '/'
        versao_http = 'HTTP/1.1'

    with open(ARQUIVO_LOG, 'a') as f:
        f.write(inicio_requisicao + ';')
        if 'User-Agent' in campos_requisicao:
            f.write(campos_requisicao['User-Agent'])
        f.write('\n')


    # Evita o uso de .. para voltar diretórios
    recurso = recurso.replace('..', ' ').replace('//', '/')

    codigo_resposta = '200'
    txt_resposta = 'OK'
    conteudo_resposta = '<h1>It works!</h1>'
    content_type = 'text/html'


    # Checa se o recurso existe e se é um arquivo ou diretório
    caminho_recurso = (diretorio + recurso).replace('//', '/')

    if os.path.isfile(caminho_recurso):
        # Descobre o MIME type do arquivo
        mime = magic.Magic(mime=True)
        content_type = mime.from_file(caminho_recurso)

        # Lê o conteúdo do arquivo
        conteudo_resposta = open(caminho_recurso, 'rb').read()
    
    elif os.path.isdir(caminho_recurso):
        listagem = ''
        for i in os.listdir(caminho_recurso):
            
            data_modificacao = time.ctime(os.path.getmtime(caminho_recurso.rstrip('/') + '/' + i))

            if os.path.isfile(caminho_recurso.rstrip('/') + '/' + i):
                tamanho_bytes = str(os.path.getsize(caminho_recurso.rstrip('/') + '/' + i))
            else:
                tamanho_bytes = '-'

            listagem += '<div class="item_listagem">'
            listagem += '<a href="' + recurso.rstrip('/') + '/' + i + '">' + i + '</a>'
            listagem += '<span class="tam_bytes">' + tamanho_bytes + '</span>'
            listagem += '<span class="mod_date">' + data_modificacao + '</span>'
            listagem += '</div>'

        conteudo_resposta = HTML_LISTAGEM.format(
            'Listagem de diretório de ' + caminho_recurso, 
            listagem,
            '<a href="../">..</a>' if caminho_recurso.rstrip('/') != diretorio.rstrip('/') else ''
        )
    
    else:
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

        print('Aguardando conexão em {0}:{1}'.format(ip_servidor, porta))

        con, info_cliente = s.accept()

        print('Conexão efetuada por', ':'.join([str(i) for i in info_cliente]), '\n')

        with open(ARQUIVO_LOG, 'a') as f:
            f.write(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S') + ';')
            f.write(':'.join([str(i) for i in info_cliente]) + ';')

        # Processa a requisição em uma thread paralela
        Thread(target=processa_requisicao, args=(con, )).start()