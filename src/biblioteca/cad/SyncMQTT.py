from abc import abstractmethod
import json

from paho.mqtt import client as mqtt_client

from biblioteca.cad.Usuario import Usuario
from biblioteca.gRPC import cadastro_pb2
from biblioteca import lib
from biblioteca.lib import CRUD

class SyncMQTTOps():
    @abstractmethod
    def criarUsuario(self, request: cadastro_pb2.Usuario, propagate: bool) -> cadastro_pb2.Status:
        pass
   
    @abstractmethod
    def atualizarUsuario(self, request: Usuario, propagate: bool) -> cadastro_pb2.Status:
        pass
    
    @abstractmethod
    def deletarUsuario(self, request: cadastro_pb2.Identificador, propagate: bool) -> cadastro_pb2.Status:
        pass

class SyncMQTT():
    """Funções que garantem que o estado dos diversos servidores esteja coerente"""

    def __init__(self, porta: int, portalCadastroServicer: SyncMQTTOps, mqtt: mqtt_client.Client) -> None:
        self.porta = porta
        self.portalCadastroServicer = portalCadastroServicer
        self.mqtt = mqtt
        self.mqtt.subscribe("cad_server/#")

        @self.mqtt.topic_callback("cad_server/usuario/"+CRUD.criar)
        def _(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            payload = json.loads(msg.payload.decode())
            if payload['remetente'] == self.porta:
                return
            
            user = cadastro_pb2.Usuario(cpf=payload['cpf'], nome=payload['nome'])
            self.portalCadastroServicer.criarUsuario(user, False)

        @self.mqtt.topic_callback("cad_server/usuario/"+CRUD.atualizar)
        def _(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            payload = json.loads(msg.payload.decode())
            if payload['remetente'] == self.porta:
                return
            
            user = Usuario(cadastro_pb2.Usuario(cpf=payload['cpf'], nome=payload['nome']), payload['bloqueado'])
            self.portalCadastroServicer.atualizarUsuario(user, False)

        @self.mqtt.topic_callback("cad_server/usuario/"+CRUD.deletar)
        def _(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
            payload = json.loads(msg.payload.decode())
            if payload['remetente'] == self.porta:
                return
            
            self.portalCadastroServicer.deletarUsuario(cadastro_pb2.Identificador(id=payload['cpf']), False)

        self.mqtt.loop_start()


    def pubUsuario(self, msg: Usuario, operacao: str):
        """Publicar uma operação de usuário no broker MQTT"""
        payload = json.dumps({
            'remetente': self.porta,
            'cpf': msg.usuario_pb2.cpf,
            'nome': msg.usuario_pb2.nome,
            'bloqueado': msg.bloqueado
        })
        self.mqtt.publish("cad_server/usuario/" + operacao, payload)