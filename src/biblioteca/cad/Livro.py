from dataclasses import dataclass
from biblioteca.gRPC import cadastro_pb2

@dataclass
class Livro():
    livro_pb2: cadastro_pb2.Livro
    emprestado: bool = False
    emprestado_para: str = None
    momento_emprestimo: float = None

    def isValido(self) -> bool:
        # Adicione validações específicas para o livro
        return all(
            [ len(self.livro_pb2.isbn) == 13,  # Supondo que o ISBN seja de 13 dígitos
              self.livro_pb2.isbn.isdigit() ]  # O ISBN deve ser numérico
        )
    
    def __hash__(self) -> int:
        return hash(self.livro_pb2.isbn)
    
    def __eq__(self, value: object) -> bool:
        if isinstance(value, Livro):
            return self.livro_pb2.isbn == value.livro_pb2.isbn
        if isinstance(value, cadastro_pb2.Livro):
            return self.livro_pb2.isbn == value.isbn
        return False