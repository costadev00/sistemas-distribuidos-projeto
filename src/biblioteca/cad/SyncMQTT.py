from dataclasses import dataclass
import dataclasses
from paho.mqtt import client as mqtt_client
import json

from biblioteca.cad.Usuario import Usuario
from biblioteca.gRPC import cadastro_pb2, cadastro_pb2_grpc
from biblioteca import lib
from biblioteca.lib import CRUD

class SyncMQTT():
    def __init__(self, porta: int, portalCadastroServicer: cadastro_pb2_grpc.PortalCadastroServicer) -> None:
        self.porta = porta
        self.portalCadastroServicer = portalCadastroServicer
        self.mqtt_user = lib.connect_mqtt("cad_server", self.porta)
        self.mqtt_user.subscribe("cad_server/#")

        @self.mqtt_user.topic_callback("cad_server/usuario/"+CRUD.criar)
        def user_on_message(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            payload = json.loads(msg.payload.decode())
            if payload['remetente'] == self.porta:
                return
            
            user = Usuario(cadastro_pb2.Usuario(cpf=payload['cpf'], nome=payload['nome']), payload['bloqueado'])
            self.portalCadastroServicer.NovoUsuario(user.usuario_pb2, None)

        self.mqtt_user.loop_start()


    def pubUsuario(self, msg: Usuario, operacao: str):
        payload = json.dumps({
            'remetente': self.porta,
            'cpf': msg.usuario_pb2.cpf,
            'nome': msg.usuario_pb2.nome,
            'bloqueado': msg.bloqueado
        })
        self.mqtt_user.publish("cad_server/usuario/" + operacao, payload)