import sys

import grpc

from biblioteca import lib
from biblioteca.gRPC import cadastro_pb2, cadastro_pb2_grpc

def run():
    porta = int(sys.argv[1])
    stub = connect_stub(porta)
    status = stub.NovoUsuario(cadastro_pb2.Usuario(cpf="123.456.789-01", nome="Jão"))
    print(status)

def connect_stub(porta: int) -> cadastro_pb2_grpc.PortalCadastroStub:
    channel = grpc.insecure_channel(f"localhost:{porta}")
    return cadastro_pb2_grpc.PortalCadastroStub(channel)

if __name__ == '__main__':
    run()