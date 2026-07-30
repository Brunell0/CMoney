# CMoney

Sistema desktop de **gestão de finanças empresariais**, desenvolvido em Python como projeto da disciplina de Programação Orientada a Objetos.

Permite controlar receitas e despesas por categoria (com teto de verba e bloqueio), gerenciar uma lista de compras, auditar operações via log e exportar relatórios em CSV — tudo com autenticação de usuários por perfil (Gerente / Funcionário).

## Tecnologias

- **Python 3** + **Tkinter** (interface gráfica)
- **JSON** como banco de dados (`banco_dados.json`)
- Arquitetura **MVC**

## Estrutura do projeto

```
CMoney/
├── main.py                    # Ponto de entrada da aplicação
├── banco_dados.json           # "Banco de dados" em JSON
├── models/                    # Entidades e acesso a dados em memória
│   ├── usuario.py             # Usuario
│   ├── transacao.py           # Categoria, Transacao (Receita/Despesa)
│   ├── database_models.py     # ItemCompra, RegistroLog
│   └── db.py                  # Db: coleções em memória (fonte única de dados)
├── controllers/                # Regras de negócio
│   ├── system_controller.py    # Fachada: orquestra todos os demais controllers
│   ├── db_controller.py        # Único ponto de acesso/escrita ao Db + persistência JSON
│   ├── login_controller.py     # Autenticação
│   ├── registration_controller.py  # Cadastro/remoção de usuários
│   ├── category_controller.py  # CRUD de categorias e verbas
│   ├── shopping_controller.py  # CRUD da lista de compras
│   ├── transaction_controller.py   # CRUD de transações e cálculo de saldo
│   └── log_controller.py       # Registro de auditoria
└── views/                      # Telas (Tkinter)
    ├── auth_view.py             # Login / cadastro
    ├── main_view.py              # Tela principal (abas)
    ├── registros_view.py         # Aba de transações
    ├── gerencia_view.py          # Aba de categorias (restrita a Gerente)
    ├── compras_view.py           # Aba de lista de compras
    ├── logs_view.py              # Aba de auditoria (restrita a Gerente)
    └── relatorios_view.py        # Exportação de relatório em CSV
```

### Arquitetura MVC

- **Model**: entidades puras (`Usuario`, `Transacao`/`Receita`/`Despesa`, `Categoria`, `ItemCompra`, `RegistroLog`) e o `Db`, que guarda tudo em memória em dicionários.
- **Controller**: `SystemController` é a única fachada que as Views enxergam — ele monta a árvore de dependências (`DbController`, `LoginController`, `CategoryController` etc.), mantém o usuário logado e repassa a autoria das ações para o `LogController`. Cada sub-controller cuida de uma responsabilidade só; nenhum deles acessa o `Db` diretamente, apenas via `DbController`.
- **View**: telas Tkinter que só conversam com o `SystemController`, sem conhecer a estrutura interna de dados.

## Como executar

Pré-requisitos: Python 3.10+ (usa `tkinter`, já incluso na instalação padrão do Python no Windows/Mac; no Linux pode exigir `sudo apt install python3-tk`).

```bash
cd CMoney
python main.py
```

Na primeira execução, o sistema cria automaticamente `banco_dados.json` com categorias e usuários padrão:

| Usuário | Senha | Perfil |
|---|---|---|
| `admin` | `admin` | Gerente |
| `user`  | `user`  | Funcionário |

> Usuários **Gerente** têm acesso às abas de **Gerência** (categorias/verbas) e **Logs de Auditoria**; **Funcionário** tem acesso a Registros, Compras e Relatórios.

## Equipe

- Bruno Antonello
- Felipe Lima
- João Marcelo Turolla
- Vitória Akemi Nakai
