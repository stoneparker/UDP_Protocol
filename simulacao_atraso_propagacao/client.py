#UDP Client
import socket
import random
import time
import sys
import atexit

client = None
addr = None
connectedWithServer = False

#Função que gerar um número aleatório
def generateRandomNumber(begin_number, number_of_decimals):
    random_int = random.randrange(begin_number, ((10**number_of_decimals) -1))
    return random_int

#Função para adicionar um cabeçalho IP e enviar o pacote para o roteador
def sendPacket(address, message):
    #Obtém endereço da instância
    source_ip = client.getsockname()
    source_ip = source_ip[0] + ":" + str(source_ip[1])

    #Adiciona o cabeçalho IP no pacote
    destination_ip = address[0] + ":" + str(address[1])
    IP_header = source_ip + "|" + destination_ip
    packet = IP_header + "|" + message

    #Envia o pacote para o roteador
    router = ("127.0.0.1", 8100)
    client.sendto(packet.encode("utf-8"), router)

#Função que decodifica o pacote do roteador
def receivePacket():
    #Recebe a mensagem do cliente
    packet, _ = client.recvfrom(1024)

    #Converte a mensagem recebida
    message = packet.decode("utf-8").split("|")
    
    # Obtém o endereço de origem
    ip_source = message[0].split(":")
    address = (ip_source[0], ip_source[1])

    # Retorna o conteúdo da mensagem e o endereço de origem
    return message[2], address

#Função que envia solicitação de conexão para o servidor
def connectWithServer(client_id):
    message = "connect-" + str(client_id)

    sendPacket(addr, message)
    print(f"Mensagem enviada para o servidor: {message}")

#Função executada antes do programa ser finalizado
def exitHandler():
    if not connectedWithServer: return

    message = "disconnect-" + str(client_id)

    sendPacket(addr, message)
    print(f"Mensagem enviada para o servidor: {message}")

#Registro da função executada antes do programa ser finalizado
atexit.register(exitHandler)

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 4455
    addr = (host, port)

    #AF_INET = indica que é um protocolo de endereço ip
    #SOCK_DGRAM = indica que é um protocolo da camada de transporte UDP
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #Vincula uma porta ao cliente
    client.bind(("127.0.0.1", 0))

    #Gera identificador do cliente
    client_id = generateRandomNumber(
        begin_number = 1,
        number_of_decimals = random.randrange(1, 10)
    )

    #Envia solicitação de conexão para o sevidor
    connectWithServer(client_id)

    #Recebe a mensagem do servidor
    msg_received_string, address = receivePacket()

    # Verifica resposta de conexão enviada pelo servidor
    if msg_received_string == "connected":
        print("Conexao estabelecida com o servidor")
        connectedWithServer = True
    else:
        print("Conexao nao estabelecida com o servidor")

        #Encerra o programa caso conexão não tenha sido estabelecida
        sys.exit()

    while True:
        #Reseta variáveis
        msg_to_answer = ""
        msg_received_string = ""

        #Gera número aleatório de até 10 casas
        random_int_to_send = generateRandomNumber(
            begin_number = 1,
            number_of_decimals = random.randrange(1, 10)
        )

        #Converte o número para string e envia com o tipo message
        msg_to_send = "message-" + str(random_int_to_send)
        print(f"Mensagem enviada para o servidor: {msg_to_send}")

        #Envia a mensagem para o servidor
        sendPacket(addr, msg_to_send)

        #Recebe a mensagem do servidor
        msg_received_string, address = receivePacket()

        print(f"Mensagem recebida do servidor: {msg_received_string}")

        #Envia mensagem para o servidor com o tipo message
        msg_to_send = "message-" + msg_received_string + " ACK"
        print(f"Mensagem enviada para o servidor: {msg_to_send}")

        #Envia a mensagem para o servidor
        sendPacket(addr, msg_to_send)

        #Fecha a conexão e aguarda 10 segundos
        
        if(msg_received_string.__contains__("Janela de Recepção: 0")):
            for i in range(10):
                print(str(10-i) + "s")
                time.sleep(1)
        else:
            for i in range(3):
                print(str(10-i) + "s")
                time.sleep(1)

