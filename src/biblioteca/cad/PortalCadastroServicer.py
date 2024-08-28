from dataclasses import dataclass
from paho.mqtt import client as mqtt_client

from biblioteca.cad.Usuario import Usuario
from biblioteca.gRPC import cadastro_pb2, cadastro_pb2_grpc
from biblioteca.cad.SyncMQTT import SyncMQTT, CRUD, SyncMQTTOps

class PortalCadastroServicer(cadastro_pb2_grpc.PortalCadastroServicer, SyncMQTTOps):
    def __init__(self, usuarios: set[Usuario], porta: int) -> None:
        super().__init__()
        self.usuarios = usuarios
        self.syncMQTT = SyncMQTT(porta, self)

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