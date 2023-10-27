#!/bin/bash

venv_dir="venv"

# Verifique se o ambiente virtual existe
if [ ! -d "$venv_dir" ]; then
    echo "Ambiente virtual não encontrado. Criando ambiente virtual..."
    python -m venv "$venv_dir"
    echo "Ambiente virtual criado."
else
    echo "Ambiente virtual encontrado."
fi

# Ative o ambiente virtual
source "$venv_dir/bin/activate"

# Instale as dependências a partir do requirements.txt
pip install -r requirements.txt

# Execute o aplicativo com Uvicorn
uvicorn main:app --reload
