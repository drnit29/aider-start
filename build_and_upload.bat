@echo off
REM build_and_upload.bat - Script para construir e fazer upload do pacote aider-start para o PyPI

echo Limpando builds anteriores...
rmdir /s /q dist build aider_start.egg-info 2>nul

echo Instalando ferramentas de build...
python -m pip install --upgrade build twine

echo Construindo o pacote...
python -m build

echo.
echo Pacote construído! Os arquivos estão na pasta 'dist/'
echo Para fazer upload para o PyPI, execute:
echo python -m twine upload dist/*

REM Comentado por segurança - descomente quando estiver pronto para publicar
REM echo Fazendo upload para o PyPI...
REM python -m twine upload dist/*

echo.
echo Pronto!
pause 