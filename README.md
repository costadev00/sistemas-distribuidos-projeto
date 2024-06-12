# sistemas-distribuidos-projeto
Projeto da disciplina de sistemas de distribuído. O projeto consiste em implementar um Sistema de Bibliotecas com armazenamento chave-valor (key-value store = KVS).

Tabela Hash ID -> DADOS.

(K,V)= Chave K possui o valor V (String).
# Portal cadastro:
Cadastro de usuário e livro.(Menu Terminal).

rpc NovoUsuario(Usuario) returns (Status) {} = Cliente: Dados / Servidor: retorna 0 para sucesso (campo maior que 3), Erro: 1 com descrição do erro.

rpc EditaUsuario(Usuario) returns (Status) {} = Cliente: Dados / Servidor: retorna 0 para sucesso (campo maior que 3), Erro: 1 com descrição do erro.

rpc RemoveUsuario(Identificador) returns (Status) {} = Cliente: Key / Servidor: retorna 0 para sucesso, Erro: 1 com descrição do erro.

rpc ObtemUsuario(Identificador) returns (Usuario) {} = Cliente: Key / Servidor: retorna Dados para sucesso, Erro: Usuario com dados em branco. 

rpc ObtemTodosUsuarios(Vazia) returns (stream Usuario) {} = Cliente: invoca método sem argumentos / Servidor: retorna lista de todos os usuários cadastrados.

(O programa não pode crashar).

# Portal biblioteca:
Emprestimo de livros a usuarios
(Menu Terminal)


