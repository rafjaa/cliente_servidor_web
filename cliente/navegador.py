import mimetypes
import socket
import sys

TIMEOUT_CONEXAO = 10
TIMEOUT_LEITURA = 1

def formata_consulta(url):
    dados_consulta = {
        'ip': '',
        'porta': 80,
        'recurso': '/'
    }

    # Remove http:// e https:// do início caso seja domínio
    url = url.lstrip('http://')
    url = url.lstrip('https://')

    # Remove a barra do domínio em casos 
    # como https://www.google.com/:8000
    url = url.replace('/:', ':')

    # Separa o host e o recurso solicitado
    partes = url.split('/')

    dominio = url.split('/')[0]

    # Verifica se há porta
    if ':' in dominio:
        dados_consulta['porta'] = int(dominio.split(':')[-1])
        dominio = dominio.split(':')[0]

    # Converte o domínio para IP, caso seja domínio
    try:
        dados_consulta['ip'] = socket.gethostbyname(dominio)
    except:
        return {}

    # Verifica se há recurso solicitado
    if len(partes) > 1:
        dados_consulta['recurso'] = '/' + '/'.join(url.split('/')[1:])

    return dados_consulta



if __name__ == '__main__':

    # Obtém a URL por linha de comando
    try:
        URL = sys.argv[1]

        dados_consulta = formata_consulta(URL)

        if not dados_consulta:
            print('Forneça um endereço válido.')
            sys.exit()
    except:
        print('Modo de uso: python3 navegador.py endereco_site')
        sys.exit()


    HOST = dados_consulta['ip']
    PORT = dados_consulta['porta']
    RECURSO = dados_consulta['recurso']

    print('\nCONSULTA\n--------')
    print('URL:', URL)
    print('IP:', HOST)
    print('PORTA:', PORT)

    # Formata o cabeçalho
    header = 'GET {0} HTTP/1.1\nHost: {1}\nUser-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36\n\n'.format(RECURSO, HOST).encode()

    # Instancia o socket TCP IPv4
    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )
    try:
        s.settimeout(TIMEOUT_CONEXAO)

        # Conecta-se ao servidor
        s.connect((HOST, PORT)) 
    except socket.timeout:
        print('\nTIMEOUT: o servidor não respondeu a requisição\n')
        sys.exit()

    # Envia a requisição
    s.send(header)

    dados = b''

    try:
        while True:
            s.settimeout(TIMEOUT_LEITURA)
            resp = s.recv(2048)

            if not len(resp):
                break

            dados += resp
    except:
        # Timeout
        pass
    finally:
        s.close()


    # Separa o cabeçalho da resposta HTTP dos dados
    sep = b'\r\n\r\n'
    if sep not in dados:
        sep = b'\n\n'

    cabecalho = dados.split(sep)[0].decode()
    conteudo = dados[len(cabecalho) + len(sep):]   


    # Obtém o código HTTP de resposta e descobre o tipo do conteúdo
    content_type = False
    codigo_resposta = False
    texto_codigo_resposta = False


    for l in cabecalho.splitlines():
        if not codigo_resposta:
            partes_cod_resposta = l.strip().split(' ')
            codigo_resposta = partes_cod_resposta[1]
            texto_codigo_resposta = ' '.join(partes_cod_resposta[2:])

        if 'Content-Type' in l:
            content_type = l.split(':')[1].replace(' ', '').split(';')[0]

    try:
        extensao_arquivo = mimetypes.guess_extension(content_type)
    except:
        extensao_arquivo = '.html'


    print('\nRESPOSTA\n--------')
    print('CÓDIGO:', codigo_resposta, '({0})'.format(texto_codigo_resposta))

    if codigo_resposta != '200':
        print()
        sys.exit()

    print('CONTENT-TYPE:', content_type, '({0})'.format(extensao_arquivo))    

    if RECURSO != '/':
        nome_arquivo = RECURSO.split('/')[-1].split('.')[0]
    else:
        nome_arquivo = URL.lstrip('http://').split('/')[0]

    # Salva o conteúdo
    with open(nome_arquivo + extensao_arquivo, 'wb') as f:
        f.write(conteudo)

    print('ARQUIVO SALVO:', nome_arquivo + extensao_arquivo)
    print()