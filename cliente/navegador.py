import socket
import sys

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
        else:
            print(dados_consulta)
    except:
        print('Modo de uso: python3 navegador.py endereco_site')
        sys.exit()


    HOST = dados_consulta['ip']
    PORT = dados_consulta['porta']
    RECURSO = dados_consulta['recurso']

    # Formata o cabeçalho
    header = 'GET {0} HTTP/1.1\nHost: {1}\n\n'.format(RECURSO, HOST).encode()

    # Instancia o socket TCP IPv4
    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    s.connect((HOST, PORT))

    try:
        s.send(header)

        print(s.recv(1024))

    finally:
        s.close()