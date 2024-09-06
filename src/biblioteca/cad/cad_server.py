import time
from concurrent import futures
import sys
import grpc

# from biblioteca.cad.PortalCadastroServicer import PortalCadastroServicer

from biblioteca.gRPC import cadastro_pb2_grpc, cadastro_pb2
from .PortalCadastroServicer import PortalCadastroServicer
from biblioteca.cad.Usuario import Usuario
from biblioteca.cad.Livro import Livro

class BibliotecaServicer(cadastro_pb2_grpc.BibliotecaServicer):
    def __init__(self, usuarios, livros):
        self.usuarios = usuarios
        self.livros = livros

    def ListarLivros(self, request, context):
        for livro in self.livros:
            yield livro.livro_pb2

    def PesquisarLivros(self, request, context):
        termos = request.termo.split('&')
        termos = [termo.split(':') for termo in termos]
        for livro in self.livros:
            match = True
            for termo in termos:
                campo, valor = termo
                if campo == 'isbn' and valor not in livro.livro_pb2.isbn:
                    match = False
                elif campo == 'titulo' and valor not in livro.livro_pb2.titulo:
                    match = False
                elif campo == 'autor' and valor not in livro.livro_pb2.autor:
                    match = False
            if match:
                yield livro.livro_pb2

    def ListarUsuarios(self, request, context):
        for usuario in self.usuarios:
            yield usuario.usuario_pb2

    def PesquisarUsuarios(self, request, context):
        termo = request.termo.lower()
        for usuario in self.usuarios:
            if termo in usuario.usuario_pb2.nome.lower() or termo in usuario.usuario_pb2.email.lower():
                yield usuario.usuario_pb2

    def EmprestarLivro(self, request, context):
        cpf_usuario = request.cpf_usuario
        titulo_livro = request.titulo_livro

        usuario = next((u for u in self.usuarios if u.usuario_pb2.cpf == cpf_usuario), None)
        livro = next((l for l in self.livros if l.livro_pb2.titulo == titulo_livro), None)

        if usuario is None:
            return cadastro_pb2.Resposta(mensagem="Usuário não encontrado")
        if livro is None:
            return cadastro_pb2.Resposta(mensagem="Livro não encontrado")
        if usuario.bloqueado:
            return cadastro_pb2.Resposta(mensagem="Usuário está bloqueado")
        if livro.emprestado:
            return cadastro_pb2.Resposta(mensagem="Livro já está emprestado")

        # Lógica de empréstimo
        livro.emprestado = True
        livro.emprestado_para = cpf_usuario
        livro.momento_emprestimo = time.time()
        return cadastro_pb2.Resposta(mensagem="Livro emprestado com sucesso")

    def BloquearUsuario(self, request, context):
        cpf_usuario = request.cpf_usuario
        usuario = next((u for u in self.usuarios if u.usuario_pb2.cpf == cpf_usuario), None)

        if usuario is None:
            return cadastro_pb2.Resposta(mensagem="Usuário não encontrado")

        # Verificar se o usuário deve ser bloqueado
        for livro in self.livros:
            if livro.emprestado_para == cpf_usuario:
                if time.time() - livro.momento_emprestimo > 10:
                    usuario.bloqueado = True
                    return cadastro_pb2.Resposta(mensagem="Usuário bloqueado por atraso na devolução")

        return cadastro_pb2.Resposta(mensagem="Usuário não possui atrasos")

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