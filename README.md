# SDK Betnacional - Python Client (Stealth Automation)

Este é um cliente modular e robusto escrito em Python projetado para integrar a plataforma Betnacional a microsserviços externos de inteligência de apostas (AI / Estratégias). 

Ele realiza a replicação completa do fluxo de autenticação (OAuth2/Keycloak + NextAuth) mimetizando perfeitamente um navegador Chrome real (evitando bloqueios Cloudflare), realiza a raspagem em tempo real usando Playwright (bypassando restrições de WebSocket) e expõe métodos de alto nível para consulta de saldo, listagem de mercados/odds e submissão automatizada de apostas (simples e múltiplas) com validação de geolocalização.

---

## 🛠️ Arquitetura do Projeto

O projeto segue um padrão profissional de design, separando as responsabilidades de comunicação de rede, motores de raspagem, autenticação e models estruturados (Pydantic):

```
client_betnacional/
│
├── .env                          # Credenciais e geolocalização do usuário (Ignorado no Git)
├── .env.example                  # Arquivo de exemplo com as variáveis configuráveis
├── .gitignore                    # Exclusões de repositório (exclui .env, venv e caches)
├── requirements.txt              # Bibliotecas de dependências do Python
├── README.md                     # Documentação principal (SDK Manual)
│
├── betnacional/                  # Pacote core do cliente
│   ├── __init__.py               # Inicializador do pacote e exportações
│   ├── client.py                 # Interface principal (Facade principal do SDK)
│   ├── config.py                 # Carregamento centralizado de configurações (.env)
│   ├── exceptions.py             # Tratamento de exceções personalizadas
│   ├── api.py                    # Cliente HTTP base com impersonation (curl_cffi)
│   ├── auth.py                   # Gerenciamento da autenticação NextAuth + Keycloak
│   ├── parser.py                 # Conversores de payload bruto para modelos Pydantic
│   ├── scraper.py                # Raspador de odds via Playwright headless
│   └── models/                   # Modelos de dados fortemente tipados (Pydantic)
│       ├── auth.py               # Estruturação de dados de sessão e usuário
│       ├── odds.py               # Estruturação de partidas, mercados e seleções
│       └── bet.py                # Estruturação de requisições de aposta e bilhetes
│
├── mitm_capture/                 # Addon e arquivos da captura original de fluxos
│   └── captured_flows.json
│
└── examples/                     # Exemplos demonstrativos do SDK
    ├── login_example.py          # Demonstração de login e checagem de saldo
    ├── betting_example.py        # Demonstração de scraping de odds e aposta simples
    └── strategy_example.py       # Exemplo de integração simulando a Inteligência
```

---

## 🔒 Configurações e Geolocalização (.env)

A Betnacional valida a localização geográfica do dispositivo ao registrar um bilhete de aposta. Para evitar bloqueios do provedor, configure os parâmetros correspondentes ao local usual de acesso nas variáveis do `.env`:

Crie um arquivo `.env` com base no arquivo [.env.example](file:///c:/Users/Renan/PythonProjects/client_betnacional/.env.example):

```env
# Credenciais da conta
BETNACIONAL_CPF="SEU_CPF"
BETNACIONAL_PASSWORD="SUA_SENHA"

# Geolocalização (Exemplo: coordenadas de acesso do navegador)
BETNACIONAL_LATITUDE=-20.044535977536334
BETNACIONAL_LONGITUDE=-41.68838661069125
BETNACIONAL_ACCURACY=137
```

---

## 🚀 SDK Manual (Métodos de Uso)

Abaixo estão explicados os métodos públicos expostos pelo facade principal `BetnacionalClient`:

### Inicialização e Autenticação

```python
from betnacional.client import BetnacionalClient

# Inicializa o cliente com raspagem headless (oculta janela do Playwright)
client = BetnacionalClient(headless_scraper=True)

# Efetua login automático gerenciando cookies de sessão e CSRF
if client.login():
    print("Autenticação efetuada com sucesso!")
```

### 1. Obter Saldo (`get_balance`)
Retorna o saldo atualizado da conta em reais (BRL).
```python
saldo = client.get_balance()
print(f"Saldo: R$ {saldo:.2f}")
```

### 2. Listar Jogos Disponíveis (`listar_jogos_rodada_brasileirao`)
Faz a raspagem dinâmica em tempo real da página do Brasileirão Série A, ordena cronologicamente por data de início do evento e retorna a lista completa de partidas e suas respectivas odds (`Resultado Final`).
```python
partidas = client.listar_jogos_rodada_brasileirao()
for match in partidas:
    print(f"[{match.id}] {match.home_team} vs {match.away_team} - Data: {match.start_time}")
```

### 3. Lançar Múltipla com Resolução de Odds (`multipla_rodada_resultados_brasileirao`)
Recebe uma lista de escolhas amigáveis mapeadas por `match_id` e a opção desejada (`"casa"`, `"empate"` ou `"fora"`). O método busca automaticamente os valores de odds atualizados no momento do clique para evitar erros de alteração de cotação.

```python
# Escolhas enviadas pela Inteligência
choices = [
    {"match_id": "66886802", "choice": "casa"},
    {"match_id": "66886814", "choice": "empate"},
    {"match_id": "66886806", "choice": "fora"},
]

# Envia a aposta múltipla de R$ 1,00 em produção
resposta = client.multipla_rodada_resultados_brasileirao(choices=choices, stake=1.00)

if resposta.success:
    print(f"Aposta efetuada! Bilhete ID: {resposta.bet_id}")
else:
    print(f"Erro ao apostar: {resposta.message}")
```

### 4. Consultar Histórico de Apostas (`get_bet_history`)
Retorna as apostas do usuário com filtro por status e período. O método consulta o endpoint `/api/v2/pending-bets` (pendentes) ou `/api/v2/settled-bets` (finalizadas).

```python
# Buscar apostas pendentes nos últimos 7 dias
historico = client.get_bet_history(
    status="pending",
    date_start="2026-05-13",
    date_end="2026-05-20"
)

for bet in historico.bets:
    print(f"[{bet.ticket_id}] {bet.home} vs {bet.away} | {bet.outcome_name} | Odd: {bet.odd} | Status: {bet.bet_status_name}")

# Buscar apostas finalizadas
finalizadas = client.get_bet_history(
    status="completed",
    date_start="2026-01-01",
    date_end="2026-05-20"
)
```

**Parâmetros:**
| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `status` | `str` | `"pending"` | `"pending"` para apostas abertas, `"completed"` para finalizadas |
| `date_start` | `str` | 30 dias atrás | Data inicial no formato `YYYY-MM-DD` |
| `date_end` | `str` | hoje | Data final no formato `YYYY-MM-DD` |
| `limit` | `int` | `20` | Limite de registros por página |
| `pagination_direction` | `str` | `"next"` | Direção da paginação |

**Retorno:** `BetHistoryResponse` contendo:
- `bets`: `List[BetHistoryItem]` — cada seleção de aposta individual
- `events`: `List[BetHistoryEvent]` — sumário dos eventos presentes nas apostas
- `scores`: `List` — placares (array vazio se não houver resultados)

---

## 🏃 Executando os Exemplos

Você pode ver os fluxos completos rodando os scripts da pasta `examples/`:

### Exemplo 1: Verificação de Login
Efetua a autenticação em 6 etapas e checa o perfil de usuário:
```powershell
python examples/login_example.py
```

### Exemplo 2: Fluxo Completo de Raspagem e Aposta
Captura as partidas em tempo real e simula o registro de um ticket:
```powershell
python examples/betting_example.py
```

### Exemplo 3: Integração da Inteligência (Múltipla por Índices)
Demonstra como o seu microsserviço externo pode listar todos os jogos, escolher pelas posições e enviar a aposta de forma amigável:
```powershell
python examples/strategy_example.py
```

---

## 📦 Implantação e Docker

Como a arquitetura foi desenhada separando o core do cliente e os motores de scraping:
1. Este cliente é ideal para ser empacotado em um container Docker rodando um serviço de API (ex: FastAPI ou Flask) que expõe os métodos de SDK.
2. A imagem Docker deve incluir o Playwright e suas dependências de sistema (`playwright install chromium` no Dockerfile) para permitir o funcionamento da raspagem headless.
