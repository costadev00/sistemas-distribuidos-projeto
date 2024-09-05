from biblioteca import lib
from biblioteca.cad.Usuario import Usuario
from biblioteca.cad.Livro import Livro
from biblioteca.gRPC import cadastro_pb2, cadastro_pb2_grpc
from biblioteca.cad.SyncMQTT import SyncMQTT, CRUD, SyncMQTTOps

# Funções do SyncMQTTOps são implementadas, e as do gRPC simplesmente as chamam
class PortalCadastroServicer(cadastro_pb2_grpc.PortalCadastroServicer, SyncMQTTOps):
    def __init__(self, usuarios: set[Usuario], livros: set[Livro], porta: int) -> None:
        super().__init__()
        self.usuarios = usuarios
        self.livros = livros
        self.mqtt = lib.connect_mqtt("cad_server", porta)
        self.syncMQTT = SyncMQTT(porta, self, self.mqtt)

    def criarUsuario(self, request: cadastro_pb2.Usuario, propagate: bool) -> cadastro_pb2.Status:
        reqU = Usuario(request)
        if not reqU.isValido():
            return cadastro_pb2.Status(status=1, msg="Usuário inválido")
        if reqU in self.usuarios:
            return cadastro_pb2.Status(status=1, msg="Usuário já existe")

        if propagate:    
            self.syncMQTT.pubUsuario(reqU, CRUD.criar)
        self.usuarios.add(reqU)
        return cadastro_pb2.Status(status=0)
    
    def NovoUsuario(self, request: cadastro_pb2.Usuario, context) -> cadastro_pb2.Status:
        return self.criarUsuario(request, True)
    
    def atualizarUsuario(self, request: Usuario, propagate: bool) -> cadastro_pb2.Status:
        usuarioExistente: Usuario | None = None
        for u in self.usuarios:
            if u == request:
                usuarioExistente = u
                break

        if usuarioExistente != None:
            if propagate:
                self.syncMQTT.pubUsuario(request, CRUD.atualizar)

            self.usuarios.remove(usuarioExistente)
            self.usuarios.add(request)
            return cadastro_pb2.Status(status=0)
        else:
            return cadastro_pb2.Status(status=1)
        
    def EditaUsuario(self, request: cadastro_pb2.Usuario, context) -> cadastro_pb2.Status:
        reqU = Usuario(request)
        return self.atualizarUsuario(reqU, True)
    
    def deletarUsuario(self, request: cadastro_pb2.Identificador, propagate: bool) -> cadastro_pb2.Status:
        usuario: Usuario | None = None
        for u in self.usuarios:
            if u.usuario_pb2.cpf == request.id:
                usuario = u
                break

        if usuario != None:
            if propagate:
                self.syncMQTT.pubUsuario(usuario, CRUD.deletar)

            self.usuarios.remove(usuario)
            return cadastro_pb2.Status(status=0)
        else:
            return cadastro_pb2.Status(status=1)
        
    def RemoveUsuario(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Status:
        return self.deletarUsuario(request, True)

    def ObtemUsuario(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Usuario:
        for usuario in self.usuarios:
            if usuario.usuario_pb2.cpf == request.id:
                return usuario.usuario_pb2
            
        return cadastro_pb2.Usuario()
    
    def ObtemTodosUsuarios(self, request: cadastro_pb2.Vazia, context):
        for usuario in self.usuarios:
            yield usuario.usuario_pb2


    def criarLivro(self, request: cadastro_pb2.Livro, propagate: bool) -> cadastro_pb2.Status:
        reqL = Livro(request)
        if not reqL.isValido():
            return cadastro_pb2.Status(status=1, msg="Livro inválido")
        if reqL in self.livros:
            return cadastro_pb2.Status(status=1, msg="Livro já existe")

        if propagate:
            self.syncMQTT.pubLivro(reqL, CRUD.criar)
        self.livros.add(reqL)
        return cadastro_pb2.Status(status=0)
    
    def NovoLivro(self, request: cadastro_pb2.Livro, context) -> cadastro_pb2.Status:
        return self.criarLivro(request, True)
    
    def atualizarLivro(self, request: Livro, propagate: bool) -> cadastro_pb2.Status:
        livroExistente = next((l for l in self.livros if l == request), None)

        if livroExistente:
            if propagate:
                self.syncMQTT.pubLivro(request, CRUD.atualizar)

            self.livros.remove(livroExistente)
            self.livros.add(request)
            return cadastro_pb2.Status(status=0)
        else:
            return cadastro_pb2.Status(status=1)
        
    def EditaLivro(self, request: cadastro_pb2.Livro, context) -> cadastro_pb2.Status:
        reqL = Livro(request)
        return self.atualizarLivro(reqL, True)
    
    def deletarLivro(self, request: cadastro_pb2.Identificador, propagate: bool) -> cadastro_pb2.Status:
        livro = next((l for l in self.livros if l.isbn == request.id), None)

        if livro:
            if propagate:
                self.syncMQTT.pubLivro(livro, CRUD.deletar)

            self.livros.remove(livro)
            return cadastro_pb2.Status(status=0)
        else:
            return cadastro_pb2.Status(status=1)
        
    def RemoveLivro(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Status:
        return self.deletarLivro(request, True)

    def ObtemLivro(self, request: cadastro_pb2.Identificador, context) -> cadastro_pb2.Livro:
        
        livro = next((l for l in self.livros if l.isbn == request.id), None)
        if livro:
            return livro.livro_pb2
        return cadastro_pb2.Livro()
    
    def ObtemTodosLivros(self, request: cadastro_pb2.Vazia, context):
        for livro in self.livros:
            yield livro.livro_pb2