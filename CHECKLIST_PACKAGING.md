# Checklist para Empacotamento e Distribuição

## Arquivos Necessários
- [x] `LICENSE` - Licença do projeto (MIT)
- [x] `README.md` - Documentação principal
- [x] `requirements.txt` - Dependências do projeto (inclui aider-chat)
- [x] `setup.py` - Configuração para instalação
- [x] `MANIFEST.in` - Lista de arquivos adicionais para incluir no pacote
- [x] `.github/workflows/python-package.yml` - Workflow do GitHub Actions para CI/CD

## Scripts de Automação
- [x] `build_and_upload.sh` - Script shell para construir e fazer upload (Linux/Mac)
- [x] `build_and_upload.bat` - Script batch para construir e fazer upload (Windows)
- [x] `install_dev.sh` - Script shell para instalação em modo de desenvolvimento (Linux/Mac)
- [x] `install_dev.bat` - Script batch para instalação em modo de desenvolvimento (Windows)

## Qualidade e Testes
- [x] Testes de unidade passando
- [x] Testes de integração passando
- [x] Versão corretamente definida no `__init__.py`
- [x] Build do pacote gerado com sucesso
- [x] Pacote instalado localmente com sucesso
- [x] Comando `aider-start` funcionando corretamente

## Pré-Publicação
- [ ] Atualizar a versão em `aider_start/__init__.py` se necessário
- [ ] Atualizar o changelog (se existir)
- [ ] Criar tag de versão no Git (ex: `git tag v0.1.0`)
- [ ] Fazer push da tag para o GitHub (ex: `git push --tags`)

## Publicação
- [ ] Executar `build_and_upload.bat` ou `build_and_upload.sh` (após descomentar a linha de upload)
- [ ] Verificar se o pacote está disponível no PyPI
- [ ] Testar a instalação a partir do PyPI (`pip install aider-start`)

## Pós-Publicação
- [ ] Anunciar o lançamento (se aplicável)
- [ ] Verificar que o fluxo de trabalho do GitHub Actions foi executado com sucesso
- [ ] Marcar próxima versão de desenvolvimento 