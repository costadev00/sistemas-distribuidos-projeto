from concurrent import futures
import sys

import grpc

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
    cadastro_pb2_grpc.add_PortalCadastroServicer_to_server(PortalCadastroServicer(usuarios), server)
    server.add_insecure_port(f"localhost:{porta}")
    server.start()
    server.wait_for_termination()

class PortalCadastroServicer(cadastro_pb2_grpc.PortalCadastroServicer):
    def __init__(self, usuarios: set[Usuario]) -> None:
        super().__init__()
        self.usuarios = usuarios

    def NovoUsuario(self, request: cadastro_pb2.Usuario, context) -> cadastro_pb2.Status:
        reqU = Usuario(request)
        if not reqU.isValido():
            return cadastro_pb2.Status(status=1, msg="Usuário inválido")
        if reqU in self.usuarios:
            return cadastro_pb2.Status(status=1, msg="Usuário já existe")
        
        self.usuarios.add(reqU)
        return cadastro_pb2.Status(status=0)
    
    def EditaUsuario(self, request: cadastro_pb2.Usuario, context) -> cadastro_pb2.Status:
        usuario: Usuario | None = None
        for u in self.usuarios:
            if u == request:
                usuario = u

        if usuario != None:
            self.usuarios.remove(usuario)
            self.usuarios.add(Usuario(request, usuario.bloqueado))
            return cadastro_pb2.Status(status=0)
        else:
            return cadastro_pb2.Status(status=1)
        
    def RemoveUsuario(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Status:
        usuario: Usuario | None = None
        for u in self.usuarios:
            if u.usuario_pb2.cpf == request.id:
                usuario = usuario.usuario_pb2

        if usuario != None:
            self.usuarios.remove(usuario)
            return cadastro_pb2.Status(status=0)
        else:
            return cadastro_pb2.Status(status=1)
    
    def ObtemUsuario(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Usuario:
        for usuario in self.usuarios:
            if usuario.usuario_pb2.cpf == request.id:
                return usuario.usuario_pb2
            
        return cadastro_pb2.Usuario()
    
    def ObtemTodosUsuarios(self, request: cadastro_pb2.Vazia, context):
        for usuario in self.usuarios:
            yield usuario.usuario_pb2

if __name__ == "__main__":
    run()