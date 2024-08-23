import sys

from biblioteca import lib

def run():
    porta = int(sys.argv[1])
    client = lib.connect_mqtt("client", porta)
    client.subscribe("topico")
    client.on_message = (lambda client, userdata, msg:
        print(f"cad_client recebeu: {msg.payload.decode()}"))
    client.loop_forever()

if __name__ == '__main__':
    run()