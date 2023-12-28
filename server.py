import socket
import json
import time
from threading import Thread, Lock
import logging

class ContaBancaria:
    def __init__(self):
        self.saldo = 10000
        self.lock = Lock()  # Lock para sincronização

    def fazer_saque(self, valor):
        with self.lock:  # Bloqueia o acesso para sincronizar o acesso ao saldo. A área crítica começa aqui
            if self.saldo >= valor:
                self.saldo -= valor
                return True
            else:
                return False
            
    # O uso do Lock é importante para garantir que apenas uma thread por vez possa modificar o saldo, evitando assim condições de corrida.

class Fila:
    def __init__(self, conta_bancaria):
        self.fila = []
        self.conta_bancaria = conta_bancaria
        self.lock = Lock()  # Lock para sincronizar a manipulação da fila.

    def add_fila(self, cliente, data):
        with self.lock:  # Bloqueia a fila para adicionar uma nova operação. A área crítica começa aqui
            self.fila.append((cliente, data))
            tamanho_fila = len(self.fila)
            logging.debug(f"Adicionado à fila: PID {data['pid']} - Tamanho da Fila: {tamanho_fila}")

    def gerenciar_processos(self):
        while True:  # Loop que processar a fila
            with self.lock:  # Bloqueia para processar um item da fila
                if self.fila:
                    cliente, data = self.fila.pop(0)  # Remove o primeiro item da fila
                    tamanho_fila = len(self.fila)
                    logging.debug(f"Processando: {tamanho_fila} na fila")
                    self.processar_saque(cliente, data)
                else:
                    logging.debug("Fila vazia. Aguardando operações...")
            time.sleep(1)  # Intervalo entre processamentos

    def processar_saque(self, cliente, data):
        hora_recebimento = time.strftime('%H:%M:%S')
        logging.debug(f"Requisição recebida às {hora_recebimento} - Processando")

        # Processa a operação de saque
        pid_aleatorio = data["pid"]
        valor_saque = data["valor"]
        sucesso = self.conta_bancaria.fazer_saque(valor_saque)

        # Prepara a resposta para o cliente
        resposta_cliente = {
            "pid": pid_aleatorio,
            "status": sucesso,
            "mensagem": "",
            "valor do saque": valor_saque
        }

        if sucesso:
            resposta_cliente["mensagem"] = f"Operação realizada com sucesso. Novo saldo: R${self.conta_bancaria.saldo}"
            logging.info(f"Saque realizado: PID {pid_aleatorio}, Valor: R${valor_saque}, Novo Saldo: R${self.conta_bancaria.saldo}")
        else:
            resposta_cliente["mensagem"] = "Saldo insuficiente. Operação não realizada."
            logging.warning(f"Saque falhou: PID {pid_aleatorio}, Valor: R${valor_saque}, Saldo Atual: R${self.conta_bancaria.saldo}")

        hora_envio = time.strftime('%H:%M:%S')
        logging.debug(f"Resposta enviada às {hora_envio}")

        cliente.send(json.dumps(resposta_cliente).encode())
        cliente.close()

def main():
    host = '127.0.0.1'
    port = 54321
    conta_bancaria = ContaBancaria()
    fila = Fila(conta_bancaria)

    logging.basicConfig(level=logging.DEBUG)

    # Thread que gerencia a fila
    thread_gerenciamento = Thread(target=fila.gerenciar_processos)
    thread_gerenciamento.start()

    # Socket do servidor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()

        logging.info(f"Servidor executando em {host}:{port}")

        while True:  #Aceitar conexões
            cliente, endereco = server_socket.accept()

            data = cliente.recv(1024).decode() 
            if data:
                fila.add_fila(cliente, json.loads(data))

if __name__ == "__main__":
    main()
