#!/usr/bin/env sh

# Defina a variável de ambiente DEBUG como 1 para mostrar informações de debug
# do script (ex: DEBUG=1 ./compile.sh)

# AVISO: É necessário um ambiente que siga o FHS para executar este script.
# (culpa do grpcio-tools)

# Interromper script se algum comando falhar
set -e

# Configuração de binários
PYTHON="python3"
PROTOC="${PYTHON} -m grpc_tools.protoc"

# Estrutura do projeto
PYTHON_SRC="src/biblioteca"
PYTHON_VENV_DIR="env"
PROTO_DIR="src/gRPC/protos"
## Caminho relativo à ${PYTHON_SRC}
PROTO_OUT_DIR="gRPC"

# Funções
isDebug() {
    [ $DEBUG ]
}

python_venv() {
    $PYTHON -m venv "${PYTHON_VENV_DIR}" && . "${PYTHON_VENV_DIR}"/bin/activate
}

clean() {
    rm -rf ${PYTHON_SRC}/${PROTO_OUT_DIR} $PYTHON_VENV_DIR ./**/*.egg-info dist
}

genRequirements() {
    $PYTHON -m pip install pip-tools
    pip-compile pyproject.toml
}

#### ENTRYPOINT ####

if isDebug; then
    printf "Shell: %s\n" "${SHELL}"
    printf "PWD: %s\n" "${PWD}"
    printf "This script: %s\n" "${0}"
fi

# Todo o script será executado com o virtual environment do Python ativado
python_venv
python -m pip install -U pip

case $1 in
    "clean" ) clean; exit ;;
    "requirements" ) genRequirements; exit ;;
    "" ) ;;
    * ) printf "Argumento não reconhecido: %s\n" $1; exit 1 ;;
esac

isDebug && printf "Instalando dependências...\n"
$PYTHON -m pip install -U wheel setuptools build
$PYTHON -m pip install -U grpcio-tools

isDebug && printf "Gerando arquivos do gRPC...\n"
$PROTOC -I${PROTO_OUT_DIR}=${PROTO_DIR} --python_out=${PYTHON_SRC} --pyi_out=${PYTHON_SRC} --grpc_python_out=${PYTHON_SRC} ${PROTO_DIR}/*.proto

isDebug && printf "Criando arquivo wheel...\n"
$PYTHON -m build

isDebug && printf "Instalando projeto...\n"
WHEEL="dist/$( ls dist | grep -e 'biblioteca.*.whl' | sed -n 1p )"
isDebug && printf "Wheel: %s\n" "${WHEEL}"
$PYTHON -m pip install --force-reinstall "${WHEEL}"