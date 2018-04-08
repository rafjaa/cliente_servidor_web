import os
import socket
import sys



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