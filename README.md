# aider-start

**Versão:** 0.1.0
**Requisito Python:** >=3.8
**Licença:** MIT (Placeholder - por favor, escolha uma licença apropriada)

## O que é o aider-start?

`aider-start` é uma ferramenta de linha de comando (CLI) projetada para simplificar o gerenciamento de presets de configuração para o [aider](https://github.com/paul-gauthier/aider), a ferramenta de programação em par com IA baseada em chat no seu terminal.

Com `aider-start`, você pode facilmente criar, editar, selecionar e executar diferentes configurações para o `aider` através de uma Interface de Usuário de Texto (TUI) interativa, tornando mais eficiente o trabalho com `aider` em diversos contextos ou projetos.

## Recursos Principais

*   **Gerenciamento de Presets:** Crie, liste, edite e exclua seus presets de configuração do `aider`.
*   **Execução Fácil:** Selecione um preset na TUI para construir e executar o comando `aider` correspondente.
*   **Assistente de Configuração:** Um assistente guiado para ajudá-lo a criar novos presets de forma intuitiva.
*   **Interface de Usuário de Texto (TUI):** Uma interface amigável no terminal para todas as operações de gerenciamento de presets.
*   **Configurações Avançadas:** Ajuste fino das configurações para cada preset.
*   **Visualização de Comando:** Revise o comando `aider` gerado antes da execução.

## Instalação

Você pode instalar o `aider-start` usando pip:

```bash
pip install aider-start
```

(Nota: Atualmente, o pacote pode não estar no PyPI. Consulte a seção "Desenvolvimento" para instalação local.)

## Uso

Para iniciar a Interface de Usuário de Texto (TUI) e gerenciar seus presets, execute:

```bash
aider-start
```

Ou explicitamente:

```bash
aider-start tui
```

A TUI permitirá que você navegue, crie, edite, exclua e execute presets do `aider`.

### Comando de Teste

Para verificar se a instalação está funcionando, você pode usar o comando `hello`:

```bash
aider-start hello
# Saída esperada: Hello World from aider-start!

aider-start hello --name SeuNome
# Saída esperada: Hello SeuNome from aider-start!
```

## Como Funciona (Visão Geral)

*   **CLI Framework:** Construído com [Typer](https://typer.tiangolo.com/) para uma interface de linha de comando robusta.
*   **Text User Interface (TUI):** Utiliza [python-prompt-toolkit](https://python-prompt-toolkit.readthedocs.io/) para criar a experiência interativa no terminal.
*   **Armazenamento de Dados:** Os presets e suas configurações são armazenados localmente em um banco de dados SQLite.
*   **Execução de Comandos:** `aider-start` constrói e executa os comandos `aider` com base nos presets selecionados.

## Desenvolvimento

Se você deseja contribuir ou executar a versão de desenvolvimento:

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/yourusername/aider-start # Atualize com o URL real
    cd aider-start
    ```

2.  **Construa e instale localmente:**
    O projeto inclui um script `build_and_test.py` para facilitar.
    ```bash
    python build_and_test.py
    ```
    Este script irá limpar builds anteriores, construir o pacote, instalá-lo em modo de desenvolvimento (`pip install -e .`) e executar um teste básico.

    Para instalar manualmente o wheel gerado (após executar `python -m build`):
    ```bash
    pip install --force-reinstall dist/*.whl
    ```

## Dependências Principais

*   [typer[all]](https://typer.tiangolo.com/)
*   [prompt-toolkit](https://python-prompt-toolkit.readthedocs.io/)
*   [PyYAML](https://pyyaml.org/) (para manipulação de arquivos de configuração do `aider`)

## Detalhes do Projeto

*   **Homepage:** *(placeholder - atualize em `pyproject.toml` e aqui)*
*   **Repositório:** *(placeholder - atualize em `pyproject.toml` e aqui)*
*   **Autores:** *(placeholder - atualize em `pyproject.toml` e aqui)*

---

*Este README foi atualizado com base na análise do código. Partes da informação de metadados são derivadas de `pyproject.toml`.*
