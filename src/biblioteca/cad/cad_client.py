import sys

import grpc

from biblioteca import lib
from biblioteca.gRPC import cadastro_pb2, cadastro_pb2_grpc

def run():
    porta = int(sys.argv[1])
    stub = connect_stub(porta)
    usuario = cadastro_pb2.Usuario(cpf="12345678901", nome="Jão")

    status = stub.NovoUsuario(usuario)
    print(status)
    status = stub.ObtemUsuario(cadastro_pb2.Identificador(id="12345678901"))
    print(status)
    status = stub.EditaUsuario(cadastro_pb2.Usuario(cpf="12345678901", nome="José"))
    print(status)
    status = stub.ObtemUsuario(cadastro_pb2.Identificador(id="12345678901"))
    print(status)

def connect_stub(porta: int) -> cadastro_pb2_grpc.PortalCadastroStub:
    channel = grpc.insecure_channel(f"localhost:{porta}")
    return cadastro_pb2_grpc.PortalCadastroStub(channel)

if __name__ == '__main__':
    run()