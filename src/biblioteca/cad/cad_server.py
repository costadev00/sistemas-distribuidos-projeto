from concurrent import futures
import sys

import grpc
from paho.mqtt import client as mqtt_client

from biblioteca.cad.PortalCadastroServicer import PortalCadastroServicer
from biblioteca.gRPC import cadastro_pb2, cadastro_pb2_grpc
from biblioteca import lib
from biblioteca.cad.Usuario import Usuario

def run():
    if len(sys.argv) != 2:
        print("Forneça a porta como argumento da linha de comando")
        return
    
    porta = int(sys.argv[1])
    usuarios: set[Usuario] = set()

    serve(porta, usuarios)

def serve(porta: int, usuarios: set[Usuario]):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cadastro_pb2_grpc.add_PortalCadastroServicer_to_server(PortalCadastroServicer(usuarios, porta), server)
    server.add_insecure_port(f"localhost:{porta}")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    run()