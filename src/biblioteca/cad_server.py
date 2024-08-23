import sys

from biblioteca import lib

def run():
    porta = int(sys.argv[1])
    client = lib.connect_mqtt("server", porta)
    client.publish("topico", "cad_server enviou mensagem")

if __name__ == '__main__':
    run()