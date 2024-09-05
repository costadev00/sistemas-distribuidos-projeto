import grpc
from biblioteca.gRPC import cadastro_pb2, cadastro_pb2_grpc

def run():
    porta = int(input("Porta do servidor: "))
    stub = connect_stub(porta)

    while True:
        print("criar")
        isbn = input("ISBN: ")
        livro = cadastro_pb2.Livro(isbn=isbn, titulo=input("Título: "), autor=input("Autor: "), total=int(input("Total: ")))

        status = stub.NovoLivro(livro)
        print(status)
        print("ler")
        status = stub.ObtemLivro(cadastro_pb2.Identificador(id=isbn))
        print(status)
        print("atualizar")
        status = stub.EditaLivro(cadastro_pb2.Livro(isbn=isbn, titulo=input("Novo título: "), autor=input("Novo autor: "), total=int(input("Novo total: "))))
        print(status)
        print("ler")
        status = stub.ObtemLivro(cadastro_pb2.Identificador(id=isbn))
        print(status)
        if input("remover? [s]") == "s":
            status = stub.RemoveLivro(cadastro_pb2.Identificador(id=isbn))
            print(status)

def connect_stub(porta: int) -> cadastro_pb2_grpc.PortalCadastroStub:
    channel = grpc.insecure_channel(f"localhost:{porta}")
    return cadastro_pb2_grpc.PortalCadastroStub(channel)

if __name__ == '__main__':
    run()
