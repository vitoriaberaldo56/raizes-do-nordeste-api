# Raízes do Nordeste — API Back-end

API REST desenvolvida como projeto multidisciplinar da disciplina de Back-end — UNINTER 2026.

## Sobre o projeto

Sistema de gerenciamento para a rede de lanchonetes **Raízes do Nordeste**, contemplando:
- Autenticação e autorização por perfis (JWT)
- Gestão de unidades e cardápio
- Controle de estoque por unidade
- Criação e acompanhamento de pedidos por múltiplos canais
- Pagamento simulado (mock)
- Programa de fidelização com conformidade LGPD

---

## Tecnologias utilizadas

| Tecnologia | Versão | Finalidade |
|---|---|---|
| Python | 3.12 | Linguagem principal |
| FastAPI | 0.115+ | Framework Web |
| SQLAlchemy | 2.0+ | ORM |
| SQLite | — | Banco de dados |
| Passlib + bcrypt | — | Hash de senha |
| Python-jose | — | JWT |
| Uvicorn | — | Servidor ASGI |

---

## Requisitos

- Python 3.12+
- pip
- Git

---

## Como executar o projeto

### 1. Clone o repositório
```bash
git clone https://github.com/vitoriaberaldo56/raizes-do-nordeste-api.git
cd raizes-do-nordeste-api
```

### 2. Crie e ative o ambiente virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

O arquivo `.env.example` já contém uma chave de teste funcional.
Basta copiar o arquivo, não é necessário editar nada para rodar localmente.
```

### 5. Inicie a API
```bash
uvicorn main:app --reload
```

A API estará disponível em: `http://localhost:8000`

---

## Documentação

Após iniciar a API, acesse:

| URL | Descrição |
|---|---|
| http://localhost:8000/docs | Swagger UI (interativo) |
| http://localhost:8000/redoc | ReDoc (alternativo) |

---

## Estrutura do projeto

```
raizes-do-nordeste-api/
│
├── app/
│   ├── domain/
│   │   ├── enums.py        # Enumerações do domínio
│   │   └── models.py       # Models do banco de dados
│   │
│   ├── application/
│   │   └── auth_service.py # Lógica de autenticação
│   │
│   ├── infrastructure/
│   │   └── database.py     # Configuração do banco
│   │
│   └── api/
│       ├── auth.py         # Endpoints de autenticação
│       ├── unidades.py     # Endpoints de unidades
│       ├── produtos.py     # Endpoints de produtos
│       ├── estoque.py      # Endpoints de estoque
│       ├── pedidos.py      # Endpoints de pedidos
│       ├── pagamentos.py   # Endpoints de pagamento mock
│       └── fidelidade.py   # Endpoints de fidelidade
│
├── main.py                 # Ponto de entrada da aplicação
├── requirements.txt        # Dependências do projeto
├── .env.example            # Exemplo de variáveis de ambiente
└── README.md               # Este arquivo
```

---

## Endpoints disponíveis

| Módulo | Método | Rota |
|---|---|---|
| Auth | POST | /auth/login |
| Auth | POST | /auth/cadastro |
| Unidades | GET | /unidades |
| Unidades | GET | /unidades/{id} |
| Produtos | GET | /produtos |
| Produtos | GET | /produtos/{id} |
| Produtos | POST | /produtos |
| Estoque | GET | /estoque |
| Estoque | POST | /estoque/entrada |
| Pedidos | POST | /pedidos |
| Pedidos | GET | /pedidos |
| Pedidos | GET | /pedidos/{id} |
| Pedidos | PATCH | /pedidos/{id}/status |
| Pagamentos | POST | /pagamentos/{id}/processar |
| Fidelidade | GET | /fidelidade/saldo |

---

## Testes

### Usando o Swagger
1. Acesse `http://localhost:8000/docs`
2. Execute `POST /auth/cadastro` para criar um usuário
3. Execute `POST /auth/login` para obter o token
4. Clique em **Authorize** (cadeado) e cole o token
5. Teste os demais endpoints

### Usando o Postman
1. Importe o arquivo `colecao_postman.json` disponível no repositório
2. Configure a variável de ambiente `base_url` como `http://localhost:8000`
3. Execute na ordem sugerida: Auth → Unidades → Produtos → Estoque → Pedidos → Pagamentos

---

## Segurança e LGPD

- Senhas armazenadas com hash bcrypt
- Autenticação via JWT com expiração de 60 minutos
- Autorização por perfis em todos os endpoints protegidos
- Consentimento LGPD registrado no cadastro
- Programa de fidelidade bloqueado sem consentimento explícito
- Respostas da API nunca expõem senha_hash

---

## Coleção Postman

O arquivo `colecao_postman.json` está disponível na raiz do repositório com todos os cenários de teste organizados por módulo.

---

## Autora

**Maria Vitória Bento Beraldo**
RU: 4676654
Curso: Análise e Desenvolvimento de Sistemas — UNINTER
Polo: Pouso Alegre - MG