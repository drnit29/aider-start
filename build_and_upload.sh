#!/bin/bash
# build_and_upload.sh - Script para construir e fazer upload do pacote aider-start para o PyPI

# Limpar builds anteriores
echo "Limpando builds anteriores..."
rm -rf dist/ build/ *.egg-info/

# Construir o pacote
echo "Instalando ferramentas de build..."
python -m pip install --upgrade build twine

echo "Construindo o pacote..."
python -m build

echo "Pacote construído! Os arquivos estão na pasta 'dist/'"
echo "Para fazer upload para o PyPI, execute:"
echo "python -m twine upload dist/*"

# Comentado por segurança - descomente quando estiver pronto para publicar
# echo "Fazendo upload para o PyPI..."
# python -m twine upload dist/*

echo "Pronto!" 