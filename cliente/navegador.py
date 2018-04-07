import socket
import sys

def formata_consulta(url):
    dados_consulta = {
        'ip': '',
        'porta': 80,
        'recurso': '/'
    }

    # Remove http:// e https:// do início caso seja domínio
    url = url.strip('http://')
    url = url.strip('https://')

    # Separa o host e o recurso solicitado
    partes = url.split('/')

    dominio = url.split('/')[0]

    # Verifica se há porta
    if ':' in dominio:
        dados_consulta['porta'] = int(dominio.split(':')[-1])
        dominio = dominio.split(':')[0]

    # Converte o domínio para IP, caso seja domínio
    dados_consulta['ip'] = socket.gethostbyname(dominio)


    # Verifica se há recurso solicitado
    if len(partes) > 1:
        dados_consulta['recurso'] = '/' + '/'.join(url.split('/')[1:])



    return dados_consulta


print(formata_consulta('https://www.google.com:8000/user/1'))