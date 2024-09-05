import grpc
from biblioteca.gRPC import cadastro_pb2, cadastro_pb2_grpc

def listar_livros(stub):
    response = stub.ListarLivros(cadastro_pb2.Vazia())
    for livro in response:
        print(f'Título: {livro.titulo}, Autor: {livro.autor}')

def pesquisar_livros(stub, termo):
    response = stub.PesquisarLivros(cadastro_pb2.Pesquisa(termo=termo))
    for livro in response:
        print(f'Título: {livro.titulo}, Autor: {livro.autor}')

def listar_usuarios(stub):
    response = stub.ListarUsuarios(cadastro_pb2.Vazia())
    for usuario in response:
        print(f'Nome: {usuario.nome}, Email: {usuario.email}')

def pesquisar_usuarios(stub, termo):
    response = stub.PesquisarUsuarios(cadastro_pb2.Pesquisa(termo=termo))
    for usuario in response:
        print(f'Nome: {usuario.nome}, Email: {usuario.email}')

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = cadastro_pb2_grpc.BibliotecaStub(channel)
        print("Listando todos os livros:")
        listar_livros(stub)
        print("\nPesquisando livros com termo 'Python':")
        pesquisar_livros(stub, 'Python')
        print("\nListando todos os usuários:")
        listar_usuarios(stub)
        print("\nPesquisando usuários com termo 'John':")
        pesquisar_usuarios(stub, 'John')

if __name__ == '__main__':
    run()