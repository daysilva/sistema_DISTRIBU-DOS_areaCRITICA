import socket
import json
import random
import time
import os

# |Saque c/PID e valores aleatórios.
def gerar_operacao(pid_aleatorio):
    valor_saque = random.randint(2, 7)
    return {
        "op": "saque",
        "pid": pid_aleatorio,
        "valor": valor_saque
    }

def main():
    server_host = '127.0.0.1'
    server_port = 54321 

    while True:  #Envia operações continuamente.
        try:
            pid_aleatorio = os.getpid()
            operacao = gerar_operacao(pid_aleatorio)  # Operação de saque.

            # Socket p/se conecta ao servidor.
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((server_host, server_port))
                client_socket.send(json.dumps(operacao).encode())

                
                resposta = client_socket.recv(1024).decode()
                if resposta:
                    print(f"Resposta recebida: {resposta}")

        except Exception as e:
            print(f"Erro no cliente: {e}")

        time.sleep(0.5)

if __name__ == "__main__":
    main()
