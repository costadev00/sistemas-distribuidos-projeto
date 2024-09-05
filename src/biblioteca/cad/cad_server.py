from concurrent import futures
import sys
import grpc

from biblioteca.cad.PortalCadastroServicer import PortalCadastroServicer
from biblioteca.gRPC import cadastro_pb2_grpc, cadastro_pb2
from biblioteca.cad.Usuario import Usuario
from biblioteca.cad.Livro import Livro

class BibliotecaServicer(cadastro_pb2_grpc.BibliotecaServicer):
    def __init__(self, usuarios, livros):
        self.usuarios = usuarios
        self.livros = livros

    def ListarLivros(self, request, context):
        for livro in self.livros:
            yield livro

    def PesquisarLivros(self, request, context):
        termo = request.termo.lower()
        for livro in self.livros:
            if termo in livro.titulo.lower() or termo in livro.autor.lower():
                yield livro

    def ListarUsuarios(self, request, context):
        for usuario in self.usuarios:
            yield usuario

    def PesquisarUsuarios(self, request, context):
        termo = request.termo.lower()
        for usuario in self.usuarios:
            if termo in usuario.nome.lower() or termo in usuario.email.lower():
                yield usuario

def run():
    if len(sys.argv) != 2:
        print("Forneça a porta como argumento da linha de comando")
        return
    
    porta = int(sys.argv[1])
    usuarios: set[Usuario] = set()
    livros: set[Livro] = set()

    serve(porta, usuarios, livros)

def serve(porta: int, usuarios: set[Usuario], livros: set[Livro]):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cadastro_pb2_grpc.add_PortalCadastroServicer_to_server(PortalCadastroServicer(usuarios, porta), server)
    cadastro_pb2_grpc.add_BibliotecaServicer_to_server(BibliotecaServicer(usuarios, livros), server)
    server.add_insecure_port(f"localhost:{porta}")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    run()