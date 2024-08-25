from concurrent import futures
import sys

import grpc

from biblioteca import lib
from biblioteca.gRPC import cadastro_pb2, cadastro_pb2_grpc

def run():
    if len(sys.argv) != 2:
        print("Forneça a porta como argumento da linha de comando")
        return
    
    porta = int(sys.argv[1])
    serve(porta)

def serve(porta: int):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cadastro_pb2_grpc.add_PortalCadastroServicer_to_server(PortalCadastroServicer(), server)
    server.add_insecure_port(f"localhost:{porta}")
    server.start()
    server.wait_for_termination()

class PortalCadastroServicer(cadastro_pb2_grpc.PortalCadastroServicer):
    def NovoUsuario(self, request: cadastro_pb2.Usuario, context) -> cadastro_pb2.Status:
        print(request)

        status = cadastro_pb2.Status(status=0)
        return status

if __name__ == "__main__":
    run()