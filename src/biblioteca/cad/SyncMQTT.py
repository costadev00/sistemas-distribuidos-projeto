from dataclasses import dataclass
import dataclasses
from paho.mqtt import client as mqtt_client
import json

from biblioteca.cad.Usuario import Usuario
from biblioteca.gRPC import cadastro_pb2, cadastro_pb2_grpc
from biblioteca import lib

class SyncMQTT():
    def __init__(self, porta: int) -> None:
        self.porta = porta
        self.mqtt_user = lib.connect_mqtt("cad_server", self.porta)

        def user_on_message(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            payload = json.loads(msg.payload.decode())
            if payload['remetente'] == self.porta:
                return
            
            user = Usuario(cadastro_pb2.Usuario(cpf=payload['cpf'], nome=payload['nome']), payload['bloqueado'])
            print(user.usuario_pb2.cpf)

        self.mqtt_user.on_message =  user_on_message
        self.mqtt_user.subscribe("cad_server/usuario")
        self.mqtt_user.loop_start()

    def pubUsuario(self, msg: Usuario, operacao: str):
        payload = json.dumps({
            'remetente': self.porta,
            'operacao': operacao,
            'cpf': msg.usuario_pb2.cpf,
            'nome': msg.usuario_pb2.nome,
            'bloqueado': msg.bloqueado
        })
        self.mqtt_user.publish("cad_server/usuario", payload)