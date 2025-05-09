@echo off
REM install_dev.bat - Script para instalar o pacote em modo de desenvolvimento

echo Instalando aider-start em modo de desenvolvimento...
pip install -e .

echo.
echo Instalação concluída! Você pode agora executar 'aider-start' no terminal.
echo.
pause 