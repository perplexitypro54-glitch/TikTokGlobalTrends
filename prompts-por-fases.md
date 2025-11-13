# 🚀 PROMPT ESTRUTURADO POR FASES - TikTok Global Trends v2.0

**Para usar com Vicode AI ou similar:**
Copie e cole cada fase sequencialmente no seu prompt.

---

## ⚠️ PRÉ-REQUISITOS

Antes de começar, tenha:
- Python 3.11+ instalado
- PostgreSQL 15+ localmente ou RDS
- Redis instalado
- Git configurado
- Conta TikTok Developer (application ID e secret)
- Conta AWS (opcional, para S3/RDS em produção)

---

# 🔴 FASE 1: SETUP & DATABASE (Semanas 1-2)

## PROMPT FASE 1.1 - Estrutura do Projeto e Dependências

```
Crie a estrutura de diretórios e arquivos iniciais para um projeto Python moderno chamado "tiktok-global-trends".

ESTRUTURA REQUERIDA:
- src/
  - __init__.py
  - main.py
  - config.py
  - api_clients/
    - __init__.py
    - tiktok_official_client.py
  - scrapers/
    - __init__.py
    - creative_center_scraper.py
  - data_processing/
    - __init__.py
    - processor.py
    - niche_classifier.py
  - storage/
    - __init__.py
    - database.py
  - orchestrator/
    - __init__.py
    - scheduler.py
  - utils/
    - __init__.py
    - logger.py
- tests/
  - __init__.py
  - test_api_client.py
  - test_processor.py
- docs/
- logs/

CRIAR TAMBÉM:
1. requirements.txt com dependências (FastAPI, SQLAlchemy, Playwright, APScheduler, etc)
2. .env.example com variáveis de ambiente necessárias
3. .gitignore
4. README.md com instruções de setup
5. pyproject.toml com metadata do projeto

O projeto deve estar pronto para instalação local com: pip install -r requirements.txt
```

---

## PROMPT FASE 1.2 - Modelo Prisma e Migrations

```
Implemente o sistema de banco de dados para o projeto TikTok Global Trends usando Prisma + PostgreSQL.

TAREFAS:
1. Criar arquivo schema.prisma com o modelo de dados completo incluindo:
   - Tabelas principais: Country, Hashtag, Video, Creator, Sound, Trend
   - Tabelas de usuários e autenticação: User, ApiKey
   - Tabelas de logs: CollectionLog, AuditLog, ComplianceLog
   - Todos os ENUMs necessários
   - Índices otimizados para queries frequentes

2. Configurar datasource PostgreSQL no schema.prisma

3. Criar script de migração: npm run prisma:generate

4. Criar arquivo database.py em src/storage/ com:
   - Classe DatabaseManager
   - Método para conectar ao PostgreSQL
   - CRUD operations básicas para Hashtag, Video, Creator
   - Connection pooling

IMPORTANTE:
- Usar PostgreSQL como database
- Implementar índices compostos em (countryId, niche), (rank, countryId), etc
- Adicionar campos de timestamp (createdAt, updatedAt)
- Implementar soft deletes onde aplicável
```

---

## PROMPT FASE 1.3 - Configuration & Environment

```
Crie o sistema de configuração centralizado para o projeto.

ARQUIVO: src/config.py

REQUISITOS:
1. Carregar variáveis de .env usando python-dotenv
2. Definir classes de configuração para cada ambiente (Development, Testing, Production)
3. Configurações necessárias:
   - TikTok API keys (client_key, client_secret)
   - PostgreSQL connection string
   - Redis connection string
   - API port (default 8000)
   - Log level
   - CORS settings
   - Compliance settings (LGPD, GDPR, CCPA regions)

4. Validação de configurações no startup
5. Logging de configuração carregada (sem expor secrets)

EXEMPLO DE .env.example:
```
ENVIRONMENT=development
DEBUG=True

# TikTok API
TIKTOK_CLIENT_KEY=your_key_here
TIKTOK_CLIENT_SECRET=your_secret_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/tiktok_trends
REDIS_URL=redis://localhost:6379

# API Server
API_PORT=8000
API_HOST=0.0.0.0

# Logging
LOG_LEVEL=INFO
LOG_DIR=./logs

# Compliance
COMPLIANCE_REGIONS=LGPD,GDPR,CCPA,PDPA
DATA_RETENTION_DAYS=365
```

Validate all required env vars on startup and raise error if missing.
```

---

## PROMPT FASE 1.4 - Logger & Utils

```
Implemente um sistema robusto de logging para o projeto.

ARQUIVO: src/utils/logger.py

REQUISITOS:
1. Logger com suporte a múltiplos níveis (DEBUG, INFO, WARNING, ERROR, CRITICAL)
2. Output em arquivos separados:
   - logs/app.log (application logs)
   - logs/errors.log (erro logs)
   - logs/audit.log (audit trail)

3. Formato de log estruturado (JSON):
   {
     "timestamp": "2025-11-13T20:00:00Z",
     "level": "INFO",
     "module": "api_client",
     "message": "Query hashtags successful",
     "country": "US",
     "duration_ms": 1234,
     "error": null
   }

4. Rotação de logs diária

5. Função get_logger(name) para importar em qualquer módulo

6. Log de performance (request duration em ms)

ADICIONAL (src/utils/__init__.py):
- Função retry_with_backoff(func, max_retries=3, base_delay=1)
- Função validate_email(email)
- Função safe_dict_get(dict, key, default=None)
- Função format_currency(value)
```

---

# 🟡 FASE 2: API CLIENT & SCRAPING (Semanas 1-2 cont)

## PROMPT FASE 2.1 - TikTok Official API Client

```
Implemente um cliente robusto para TikTok Official API com suporte a autenticação OAuth2.

ARQUIVO: src/api_clients/tiktok_official_client.py

CLASSE: TikTokAPIClient

REQUISITOS:
1. Autenticação OAuth2
   - Método get_access_token() com cache e refresh automático
   - Tokens expiram em ~1 hora
   - Cache em memória com verificação de expiração

2. Rate Limiting
   - Implementar rate limiting por país
   - USA/Brasil/México/Indonésia: 600 req/min
   - Outros países: 300 req/min
   - Respeitar headers X-RateLimit-Remaining
   - Backoff automático se rate limit excedido

3. Métodos principais:
   - query_hashtags(country, niche=None, limit=50) -> List[Dict]
   - get_video_info(video_id) -> Dict
   - get_creator_info(creator_id) -> Dict
   - get_sound_info(sound_id) -> Dict

4. Error handling
   - Retry automático com exponential backoff (3 tentativas)
   - Circuit breaker pattern
   - Log de todos os erros
   - Raise exceções customizadas (TikTokAPIError, RateLimitError, etc)

5. Timeout
   - Default 30 segundos por request
   - Configurável via constructor

ESTRUTURA ESPERADA:
class TikTokAPIClient:
    def __init__(self, client_key, client_secret, region='US')
    async def get_access_token(self) -> str
    async def query_hashtags(self, country, limit=50) -> List[Dict]
    async def _check_rate_limit(self) -> None
    async def _make_request(self, endpoint, method='GET', data=None) -> Dict
```

---

## PROMPT FASE 2.2 - Creative Center Scraper

```
Implemente o scraper para TikTok Creative Center com Playwright.

ARQUIVO: src/scrapers/creative_center_scraper.py

CLASSE: CreativeCenterScraper

REQUISITOS:
1. Navegação automática do Creative Center
   - URL base: https://ads.tiktok.com/business/creativecenter
   - Suportar países diferentes (URLs por país em constante COUNTRY_URLS)
   - Headless browser para evitar bloqueios
   - User-Agent realista

2. Métodos principais:
   - scrape_trending_hashtags(country, limit=50) -> List[Dict]
   - scrape_trending_sounds(country, limit=50) -> List[Dict]
   - scrape_trending_creators(country, limit=50) -> List[Dict]

3. Data extraction
   - Parse com BeautifulSoup4
   - Extrair: name, usage_count, engagement, growth_rate, trend_direction
   - Validação de dados extraídos
   - Tratamento de valores nulos

4. Performance
   - Timeout de 30 segundos por página
   - Cache de dados por 1 hora
   - Paralelização de múltiplas países (máx 3 simultâneos)

5. Error handling
   - Capturar falhas de carregamento de página
   - Retry automático (2 tentativas)
   - Log detalhado de erros
   - Fallback para dados cached se tudo falhar

6. Headless browser management
   - Iniciar e fechar navegador corretamente
   - Usar context managers (async with)
   - Limpar cookies/cache entre requisições

ESTRUTURA ESPERADA:
class CreativeCenterScraper:
    async def __aenter__(self)
    async def __aexit__(self)
    async def scrape_trending_hashtags(self, country, limit=50) -> List[Dict]
    async def _extract_hashtags(self, html) -> List[Dict]
    async def _validate_data(self, data) -> bool
```

---

## PROMPT FASE 2.3 - Rate Limiter & Fallback Handler

```
Implemente o sistema inteligente de rate limiting e fallback.

ARQUIVO: src/utils/rate_limiter.py

CLASSE: RateLimiter

REQUISITOS:
1. Rate limiting com token bucket algorithm
   - Por país
   - Por IP (para API REST)
   - Configurável por tipo de request

2. Backoff exponencial
   - Primeira tentativa: imediato
   - Segunda tentativa: 2 segundos
   - Terceira tentativa: 8 segundos
   - Máximo 60 segundos de espera

3. Método wait(country)
   - Aguarda tempo necessário
   - Respeita rate limit global
   - Evita exceção se rate limit próximo

ARQUIVO: src/utils/fallback_handler.py

CLASSE: FallbackHandler

REQUISITOS:
1. Pipeline de fallback para coleta de dados
   - Prioridade 1: TikTok API Oficial
   - Prioridade 2: Creative Center Scraper
   - Prioridade 3: Playwright fallback
   - Fallback 4: Use cached data da coleta anterior

2. Método get_trends(country, source_priority=None) -> Dict
   - Tenta em sequência até sucesso
   - Log qual fonte foi usada
   - Cache resultado

3. Error recovery
   - Detecta qual etapa falhou
   - Tenta próxima fonte
   - Se todas falharem, usa cache + log de erro
   - Notifica admin via alert

ESTRUTURA ESPERADA:
class RateLimiter:
    def wait(self, country: str) -> None
    def check_limit_exceeded(self, country: str) -> bool

class FallbackHandler:
    async def get_trends(self, country, niche) -> Dict
    async def _try_api_source(self, country) -> Dict
    async def _try_scraper_source(self, country) -> Dict
    async def _try_cached_data(self, country) -> Dict
```

---

# 🟢 FASE 3: DATA PROCESSING (Semana 2)

## PROMPT FASE 3.1 - Data Processor & Cleaner

```
Implemente o pipeline de processamento de dados.

ARQUIVO: src/data_processing/processor.py

CLASSE: DataProcessor

REQUISITOS:
1. Limpeza de dados (clean_data)
   - Remove duplicatas
   - Remove valores nulos
   - Valida tipos de dados
   - Padroniza formatação

2. Normalização (normalize_data)
   - Lowercase em campos de texto
   - UTF-8 encoding
   - Timezone conversion (UTC)
   - Remove whitespace extra

3. Enriquecimento (enrich_data)
   - Calcula engagementRate = (likes + comments + shares) / total_views
   - Calcula viralScore = (engagement_rate * 50) + (growth_rate * 50)
   - Detecta trend direction (UP/DOWN/STABLE)
   - Calcula ranking

4. Validação (validate_record)
   - Verifica campos obrigatórios
   - Valida types
   - Valida ranges (engagement 0-100, growth -100 a +300)
   - Retorna True/False + lista de erros

ESTRUTURA ESPERADA:
class DataProcessor:
    async def process_raw_data(self, raw_data: List[Dict], country: str) -> List[Dict]
    def clean_data(self, data: List[Dict]) -> List[Dict]
    def normalize_data(self, data: List[Dict]) -> List[Dict]
    def enrich_data(self, data: List[Dict]) -> List[Dict]
    def validate_record(self, record: Dict) -> Tuple[bool, List[str]]

Métodos devem ser eficientes e processar 100+ registros em <5 segundos.
```

---

## PROMPT FASE 3.2 - Niche Classifier

```
Implemente o classificador inteligente de nichos.

ARQUIVO: src/data_processing/niche_classifier.py

CLASSE: NicheClassifier

REQUISITOS:
1. Configuração de nichos por país
   - Arquivo: src/config/niches_by_country.yaml
   - Formato:
   ```
   US:
     booktok:
       keywords: [book, reading, author, novel, literature]
       hashtags: [#booktok, #bookstagram]
     healthtok:
       keywords: [fitness, workout, health, wellness]
       hashtags: [#healthtok, #fitnessgirl]
   BR:
     musicbtok:
       keywords: [funk, samba, música, dance]
       hashtags: [#musicbtok, #funkbrasileiro]
   ```

2. Classificação (classify)
   - Input: hashtag, title, description
   - Match com keywords
   - Calcular confidence score (0-1)
   - Retornar niche + score

3. Multi-niche support
   - Um item pode ter múltiplos nichos
   - Retornar lista de nichos ordenada por score

4. Método classify_batch
   - Classificar 100+ registros em paralelo
   - Cache de resultados

ESTRUTURA ESPERADA:
class NicheClassifier:
    def __init__(self, country: str)
    def classify(self, text: str) -> Tuple[str, float]
    def classify_batch(self, items: List[Dict]) -> List[Dict]
    def get_niches_for_country(self, country: str) -> List[str]

Retornar formato:
{
  "hashtag": "#booktok",
  "niche": "booktok",
  "confidence": 0.95,
  "alternative_niches": [("entertainment", 0.45)]
}
```

---

# 🔵 FASE 4: ORCHESTRATION (Semana 2)

## PROMPT FASE 4.1 - Scheduler Multi-País

```
Implemente o orquestrador de jobs multi-país com timezone awareness.

ARQUIVO: src/orchestrator/scheduler.py

CLASSE: GlobalTrendScheduler

REQUISITOS:
1. Configuração de países e frequência
   - Arquivo: src/config/countries.yaml
   - Cada país tem timezone definido
   - Frequência de coleta por país (4x, 6x/dia, etc)

2. Jobs agendados com APScheduler
   - Timezone-aware scheduling
   - Respeitar timezone de cada país
   - Executar coleta 4-6x por dia (configurável)

3. Exemplo de schedule:
   ```
   USA (EST timezone):
     - 6:00 AM EST
     - 12:00 PM EST
     - 3:00 PM EST
     - 9:00 PM EST

   Brasil (BRT timezone):
     - 8:00 AM BRT
     - 2:00 PM BRT
     - 5:00 PM BRT
     - 11:00 PM BRT

   Indonésia (WIB timezone):
     - 5:00 AM WIB
     - 11:00 AM WIB
     - 2:00 PM WIB
     - 8:00 PM WIB
   ```

4. Métodos principais:
   - start() - Inicia scheduler
   - stop() - Para scheduler
   - add_country_job(country, frequency) - Adiciona job para país
   - get_status() - Retorna status todos jobs
   - manual_trigger(country) - Força coleta manual

5. Error handling
   - Se job falha, tenta próxima coleta na hora programada
   - Não pula jobs
   - Log de cada execução

6. Monitoramento
   - Log último tempo de execução
   - Log próximo tempo de execução
   - Alertas se job falha 3x consecutivas

ESTRUTURA ESPERADA:
class GlobalTrendScheduler:
    def __init__(self)
    def start(self)
    def stop(self)
    async def add_country_job(self, country: str, frequency: int = 4)
    async def _execute_collection_job(self, country: str)
    def get_status(self) -> Dict
    def get_next_execution(self, country: str) -> datetime
```

---

## PROMPT FASE 4.2 - Collection Job Executor

```
Implemente a função que executa a coleta de dados para um país.

ARQUIVO: src/orchestrator/collection_job.py

CLASSE: CollectionJobExecutor

REQUISITOS:
1. Função principal: execute_collection(country: str) -> Dict
   - Coordena todo o fluxo de coleta
   - Chama API Client
   - Chama Creative Center Scraper (paralelo)
   - Aplica Fallback Handler
   - Processa dados
   - Salva em DB
   - Retorna summary

2. Fluxo:
   ```
   1. Log "Starting collection for {country}"
   2. Get credentials for country
   3. Initialize clients (API, Scraper, Fallback)
   4. Execute collection (paralelo se possível)
   5. Merge results
   6. Validate data
   7. Process data (clean, normalize, classify)
   8. Save to DB
   9. Update cache
   10. Send notifications
   11. Return summary {success: bool, records: int, duration_ms: int}
   ```

3. Parallelização
   - Coletar de API e Creative Center em paralelo
   - Aguardar ambos antes de processar
   - Timeout total 60 segundos

4. Error handling
   - Catch exceptions em cada etapa
   - Log detalhado
   - Salvar mesmo que parte falhe
   - Retry de etapa específica se falhar

5. Return format:
   ```
   {
     "country": "US",
     "status": "success|partial|failed",
     "records_collected": 150,
     "records_processed": 145,
     "records_failed": 5,
     "duration_ms": 8234,
     "timestamp": "2025-11-13T20:00:00Z",
     "sources_used": ["official_api", "creative_center"],
     "errors": []
   }
   ```

ESTRUTURA ESPERADA:
class CollectionJobExecutor:
    async def execute_collection(self, country: str) -> Dict
    async def _collect_from_sources(self, country: str) -> List[Dict]
    async def _process_and_save(self, raw_data: List[Dict], country: str) -> Dict
    async def _update_cache(self, country: str, data: List[Dict])
    async def _send_notifications(self, result: Dict)
```

---

# 🟣 FASE 5: STORAGE & API (Semana 2-3)

## PROMPT FASE 5.1 - Database Storage Layer

```
Implemente a camada de armazenamento em banco de dados.

ARQUIVO: src/storage/database.py

CLASSE: DatabaseManager

REQUISITOS:
1. Conexão com PostgreSQL
   - Connection pooling (min 5, max 20)
   - Reconexão automática se cair
   - Health check a cada 5 minutos

2. CRUD operations para Hashtag
   - create_hashtag(data: Dict) -> str (returns id)
   - get_hashtag(id: str) -> Dict
   - update_hashtag(id: str, data: Dict) -> bool
   - delete_hashtag(id: str) -> bool
   - bulk_upsert_hashtags(data: List[Dict]) -> Dict (retorna count inserted/updated)

3. CRUD para outros models (Video, Creator, Sound, Trend)
   - Mesmos métodos
   - Bulk operations otimizadas

4. Query helpers
   - get_trending_hashtags(country: str, niche: str, limit: int = 50) -> List[Dict]
   - get_creator_by_username(username: str, country: str) -> Dict|None
   - get_recent_trends(country: str, days: int = 7) -> List[Dict]

5. Performance
   - Índices em (countryId, niche)
   - Índices em rank
   - Use batch inserts onde possível
   - Prepared statements para queries

6. Transactions
   - Usar context manager: async with db.transaction()
   - Rollback automático em erro

ESTRUTURA ESPERADA:
class DatabaseManager:
    def __init__(self, connection_string)
    async def connect()
    async def disconnect()
    async def health_check() -> bool
    
    # Hashtag CRUD
    async def create_hashtag(self, data: Dict) -> str
    async def get_hashtag(self, id: str) -> Dict
    async def bulk_upsert_hashtags(self, data: List[Dict]) -> Dict
    
    # Query helpers
    async def get_trending_hashtags(self, country, niche, limit) -> List[Dict]
    
    # Transactions
    @contextmanager
    async def transaction(self)
```

---

## PROMPT FASE 5.2 - FastAPI REST API

```
Implemente a API REST com FastAPI.

ARQUIVO: src/api/main.py + routers

REQUISITOS:
1. Server FastAPI
   - Host 0.0.0.0
   - Port 8000 (configurável)
   - CORS habilitado para localhost
   - Documentação Swagger em /docs

2. Endpoints principais:
   
   GET /api/v1/trends/{country}
   - Query params: niche (opcional), limit (default 50)
   - Return: List[{hashtag, posts, views, growth, rank}]
   - Status 200/404/500
   
   GET /api/v1/trends/{country}/{niche}
   - Trends específicos de um nicho
   - Return: List[Trend]
   
   GET /api/v1/countries
   - List countries suportados
   - Return: [{code, name, users_M, growth, last_update}]
   
   GET /api/v1/health
   - Health check
   - Return: {status: ok/degraded, db: ok/fail, redis: ok/fail}
   
   POST /api/v1/export/{country}/{niche}
   - Export trends em CSV
   - Query params: format (csv/json), date_range
   - Return: File ou JSON

3. Authentication
   - API Key autenticação em header X-API-Key
   - Validar API key contra DB
   - Log acesso

4. Rate limiting
   - 100 req/min por IP
   - 1000 req/min por API key
   - Return 429 se excedido

5. Error handling
   - Exceções capturam e retornam JSON error
   - Include request_id para rastrear
   - Log de erros em Sentry

6. Middleware
   - CORS middleware
   - Logging middleware (log todas requests)
   - Error handler middleware

7. Models Pydantic
   - TrendResponse
   - CountryResponse
   - ErrorResponse
   - HealthResponse

ESTRUTURA ESPERADA:
from fastapi import FastAPI, APIRouter

app = FastAPI(title="TikTok Global Trends API", version="2.0")

@app.get("/api/v1/trends/{country}")
async def get_trends(country: str, niche: Optional[str], limit: int = 50)

@app.get("/api/v1/health")
async def health_check()

@app.get("/api/v1/countries")
async def list_countries()

@app.post("/api/v1/export/{country}/{niche}")
async def export_trends(country: str, niche: str, format: str = "csv")
```

---

# 🟠 FASE 6: FRONTEND DASHBOARD (Semana 3)

## PROMPT FASE 6.1 - React Dashboard Setup

```
Crie um dashboard web com React + TypeScript.

ARQUIVO: web/package.json + src/

REQUISITOS:
1. Setup Vite + React 18 + TypeScript
   - Template moderno
   - Pre-configured com Tailwind CSS
   - ESLint + Prettier configurados

2. Estrutura de componentes:
   ```
   src/
     components/
       TrendTable/
         TrendTable.tsx
         TrendTable.module.css
       CountrySelector/
       NicheSelector/
       TrendChart/
       ExportButton/
       HealthStatus/
     pages/
       Dashboard.tsx
       Analytics.tsx
     hooks/
       useTrends.ts
       useFetch.ts
     context/
       AppContext.tsx
     utils/
       api.ts
       formatters.ts
     App.tsx
     main.tsx
   ```

3. Páginas principais:
   - Dashboard (página inicial com trends)
   - Analytics (gráficos e estatísticas)
   - Settings (configurações do usuário)

4. Componentes:
   - CountrySelector dropdown
   - NicheSelector (dinâmico baseado no país)
   - TrendTable com sorting/filtering
   - Charts (Line, Bar, Heatmap)
   - Export button
   - Health status indicator

5. API Integration
   - Fetch trends da API
   - Retry automático em erro
   - Loading states
   - Error boundaries

USAR BIBLIOTECAS:
- React Query para state management de data
- Recharts para gráficos
- Tailwind CSS para styling
- TypeScript para type safety
```

---

## PROMPT FASE 6.2 - Dashboard Components

```
Implemente os componentes principais do dashboard.

ARQUIVO: web/src/components/

COMPONENTES:

1. TrendTable.tsx
   - Tabela com 50 trends
   - Colunas: Rank, Hashtag, Posts, Views, Growth%, Trend Direction
   - Sorting por qualquer coluna
   - Highlighting de top 10
   - Hover effects

2. CountrySelector.tsx
   - Dropdown com 15 países
   - Show users count e growth rate
   - Atualiza trends quando muda
   - Icon por país

3. NicheSelector.tsx
   - Dropdown dinâmico baseado em país
   - Show nicho popularity
   - Multi-select support

4. TrendChart.tsx
   - Line chart de top 5 trends (últimos 7 dias)
   - Recharts library
   - Legendas interativas
   - Responsivo

5. HealthStatus.tsx
   - Indicador de status (green/yellow/red)
   - Show último update por país
   - Show próximo update
   - Database connection status

6. ExportButton.tsx
   - Button para export
   - Modal com opções (CSV/JSON, date range)
   - Download file

TODOS devem ser:
- TypeScript typed
- Componentes funcionais com hooks
- Responsivos (mobile friendly)
- Acessíveis (ARIA labels)
- Bem documentados com comentários
```

---

# 🔐 FASE 7: CONFORMIDADE & SEGURANÇA (Semana 3)

## PROMPT FASE 7.1 - Compliance Manager

```
Implemente conformidade com LGPD, GDPR, CCPA, PDPA.

ARQUIVO: src/compliance/compliance_manager.py

CLASSE: ComplianceManager

REQUISITOS:
1. LGPD (Brasil)
   - Consentimento explícito no signup
   - Retenção máxima 365 dias
   - Right to delete (apagar dados pessoais)
   - Direito a acesso (exportar dados)
   - Log de acesso a dados

2. GDPR (Europa)
   - Consentimento duplo (opt-in + opt-in)
   - DPA com data processor
   - Dados residem em EU
   - Right to be forgotten (apagar dados)
   - Data portability
   - Retenção máxima 90 dias

3. CCPA (USA)
   - Disclosure de coleta clara
   - Direito a opt-out
   - Delete on request (<45 dias)
   - Don't sell my data option

4. PDPA (Ásia)
   - Dados localizados no país
   - Consentimento expresso
   - Notificação de breach em 72h

5. Métodos:
   - check_compliance(user, action) -> bool
   - delete_user_data(user_id, region) -> bool
   - export_user_data(user_id) -> File
   - log_data_access(user_id, resource, timestamp)
   - is_data_retention_expired(record_id) -> bool

6. Automático
   - Limpeza de dados expirados diariamente
   - Audit log de todas ações de compliance
   - Alertas se compliance violated

ESTRUTURA ESPERADA:
class ComplianceManager:
    def check_compliance(self, user_id: str, action: str) -> bool
    async def delete_user_data(self, user_id: str, region: str) -> bool
    async def export_user_data(self, user_id: str) -> bytes
    def log_data_access(self, user_id: str, resource: str)
    async def cleanup_expired_data(self)
```

---

## PROMPT FASE 7.2 - Security & Authentication

```
Implemente autenticação e segurança robusta.

ARQUIVO: src/auth/auth_manager.py + src/security/

REQUISITOS:
1. JWT Authentication
   - Create access token (expires em 1 hora)
   - Create refresh token (expires em 7 dias)
   - Validate token
   - Refresh token logic

2. Password hashing
   - Use bcrypt
   - Hash on create
   - Verify on login
   - Salt aleatório

3. API Key management
   - Generate API keys
   - Hash API keys no DB
   - Validate API key
   - Revoke API key

4. Endpoints de autenticação:
   POST /api/v1/auth/login
   - Input: email, password
   - Output: access_token, refresh_token, expires_in
   
   POST /api/v1/auth/refresh
   - Input: refresh_token
   - Output: access_token
   
   POST /api/v1/auth/logout
   - Invalidate tokens

5. Security headers
   - HTTPS obrigatório em produção
   - HSTS header
   - X-Content-Type-Options: nosniff
   - X-Frame-Options: DENY
   - Content-Security-Policy

6. Input validation
   - Sanitize all inputs
   - SQL injection prevention (use parameterized queries)
   - XSS prevention
   - CSRF protection (tokens)

7. Rate limiting
   - Login attempts: 5/min por IP
   - API requests: 100/min por IP, 1000/min por API key
   - Lockout após múltiplas falhas

ESTRUTURA ESPERADA:
class AuthManager:
    def create_access_token(self, user_id: str) -> str
    def validate_access_token(self, token: str) -> Dict
    def hash_password(self, password: str) -> str
    def verify_password(self, password: str, hash: str) -> bool
    def generate_api_key(self, user_id: str) -> str
    def validate_api_key(self, key: str) -> Dict
```

---

# 🧪 FASE 8: TESTING & DEPLOYMENT (Semana 3-4)

## PROMPT FASE 8.1 - Unit Tests

```
Implemente testes automatizados robustos.

ARQUIVO: tests/

REQUISITOS:
1. Framework: pytest
2. Coverage: >80% de cobertura de código

TESTES NECESSÁRIOS:

tests/test_api_client.py
- test_authentication_success
- test_authentication_expired_token_refresh
- test_rate_limit_respected
- test_retry_on_failure
- test_query_hashtags_success
- test_query_hashtags_invalid_country

tests/test_processor.py
- test_clean_data_removes_duplicates
- test_normalize_data_lowercase
- test_enrich_data_calculates_viral_score
- test_validate_record_valid_data
- test_validate_record_invalid_data

tests/test_classifier.py
- test_classify_booktok
- test_classify_unknown_niche
- test_classify_multiple_niches
- test_classify_batch_performance

tests/test_database.py
- test_connect_to_database
- test_create_hashtag
- test_bulk_upsert_hashtags
- test_query_trending_hashtags
- test_transaction_rollback_on_error

tests/test_scheduler.py
- test_add_country_job
- test_job_executes_at_right_time
- test_job_retry_on_failure
- test_manual_trigger

tests/test_api.py
- test_get_trends_success
- test_get_trends_invalid_country_404
- test_health_check
- test_export_csv
- test_api_key_validation
- test_rate_limiting

3. Mock objects
   - Mock TikTok API
   - Mock Database
   - Mock Redis
   - Mock Playwright browser

4. Fixtures
   - Sample data fixtures
   - Database fixtures (clean state)
   - API client fixtures

5. CI/CD Integration
   - Run tests on every push
   - Coverage report
   - Fail if coverage <80%

COMANDO: pytest tests/ -v --cov=src
```

---

## PROMPT FASE 8.2 - Docker & Deployment

```
Containerize a aplicação e prepare para deployment.

ARQUIVO: Dockerfile, docker-compose.yml

REQUISITOS:
1. Dockerfile
   - Base: python:3.11-slim
   - Copy requirements.txt
   - Install dependencies
   - Copy source code
   - Non-root user
   - Health check command
   - CMD: uvicorn src.api.main:app --host 0.0.0.0 --port 8000

2. docker-compose.yml
   - Service: api (FastAPI)
   - Service: postgres (RDS)
   - Service: redis (ElastiCache)
   - Volumes para persistence
   - Networks para comunicação
   - Environment variables

3. .dockerignore
   - __pycache__
   - .env
   - .git
   - venv
   - logs

4. Scripts de deployment
   - scripts/deploy-staging.sh
   - scripts/deploy-prod.sh
   - Usar AWS CLI para push ECR
   - Usar kubectl ou ECS CLI para deploy

5. Health check
   - GET /api/v1/health -> {status: ok}
   - Database connection check
   - Redis connection check
   - Timeout: 30 segundos

6. Logging & Monitoring
   - Output logs para stdout (docker capture)
   - Send errors to Sentry
   - Prometheus metrics endpoint

BUILD COMMAND:
docker build -t tiktok-trends:latest .

RUN COMMAND:
docker-compose -f docker-compose.yml up -d

PUSH TO ECR:
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker tag tiktok-trends:latest <account>.dkr.ecr.<region>.amazonaws.com/tiktok-trends:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/tiktok-trends:latest
```

---

# 📊 FASE 9: MONITORING & OPTIMIZATION (Semana 4+)

## PROMPT FASE 9.1 - Prometheus Metrics

```
Implemente monitoramento com Prometheus.

ARQUIVO: src/monitoring/metrics.py

REQUISITOS:
1. Métricas a coletar:
   - tiktok_scraper_runs_total (counter) - total de execuções
   - tiktok_scraper_failures_total (counter) - total de falhas
   - tiktok_scraper_duration_seconds (histogram) - tempo de execução
   - tiktok_records_collected (gauge) - records coletados
   - tiktok_api_requests (counter) - requests à API
   - tiktok_api_rate_limit_remaining (gauge) - rate limit restante
   - http_requests_total (counter) - total de requests HTTP
   - http_request_duration_seconds (histogram) - latência
   - database_connection_errors_total (counter) - erros de DB

2. Endpoints:
   GET /metrics -> Prometheus format

3. Exemplo Prometheus config (prometheus.yml):
   ```
   scrape_configs:
     - job_name: 'tiktok-trends'
       static_configs:
         - targets: ['localhost:8000']
       metrics_path: '/metrics'
   ```

4. Grafana dashboards
   - Dashboard 1: System Health (Uptime, Requests, Errors)
   - Dashboard 2: Collection Performance (Duration, Records, Success Rate)
   - Dashboard 3: API Usage (Rate limit, Requests/min)
   - Dashboard 4: Database Health (Connections, Queries, Latency)
```

---

## PROMPT FASE 9.2 - Performance Optimization

```
Otimize performance da aplicação.

REQUISITOS:
1. Database optimization
   - Índices em queries frequentes
   - Query optimization
   - Connection pooling
   - Denormalization onde necessário

2. Cache strategy
   - Redis cache para trends (TTL 1 hora)
   - Cache API responses (ETag support)
   - Browser cache (Cache-Control headers)

3. API optimization
   - Pagination (offset/limit)
   - Response compression (gzip)
   - Lazy loading de dados
   - Batch operations

4. Async optimization
   - Concurrent requests em paralelo
   - Background tasks (Celery)
   - Non-blocking I/O

5. Monitoring performance
   - Query time logs
   - Request latency metrics
   - Memory usage monitoring
   - CPU usage monitoring

BENCHMARKS ALVO:
- GET /trends: <2 segundos
- POST /export: <10 segundos
- Coleta de dados: <60 segundos por país
- Dashboard load: <3 segundos
- API uptime: 99.9%
```

---

# ✅ FASE 10: LAUNCH & REFINEMENT

## PROMPT FASE 10.1 - Pre-Launch Checklist

```
Verifique antes de lançar para produção.

CHECKLIST:
□ Todos testes passando (pytest coverage >80%)
□ Documentação Swagger completa
□ README com instruções de setup
□ .env.example com todas variáveis
□ Security: HTTPS, rate limiting, input validation
□ Database migrations testadas
□ Backups automáticos configurados
□ Monitoring/Alerting funcionando
□ Error tracking (Sentry) configurado
□ Logging estruturado
□ CI/CD pipeline funcionando
□ Docker image buildando sem erros
□ Compliance (LGPD/GDPR) verificada
□ Performance benchmarks OK
□ Load testing realizado
□ Security audit completo
□ Team training realizado

DEPLOY STEPS:
1. Deploy staging
2. Run smoke tests
3. Verify monitoring/logging
4. Deploy production
5. Monitor closely (24h)
6. Post-mortem meeting
```

---

# 🎯 RESUMO DE TAREFAS POR FASE

## ✅ Fase 1 (Semana 1-2): SETUP & DATABASE
- [ ] Estrutura projeto
- [ ] requirements.txt
- [ ] Schema Prisma
- [ ] Database migrations
- [ ] Config centralizado
- [ ] Logger setup

## ✅ Fase 2 (Semana 1-2): API CLIENT & SCRAPING
- [ ] TikTok API Client
- [ ] Creative Center Scraper
- [ ] Rate Limiter
- [ ] Fallback Handler

## ✅ Fase 3 (Semana 2): DATA PROCESSING
- [ ] Data Processor
- [ ] Niche Classifier
- [ ] Validation

## ✅ Fase 4 (Semana 2): ORCHESTRATION
- [ ] Global Scheduler
- [ ] Collection Jobs

## ✅ Fase 5 (Semana 2-3): STORAGE & API
- [ ] Database Storage
- [ ] FastAPI REST API
- [ ] Endpoints

## ✅ Fase 6 (Semana 3): FRONTEND
- [ ] React Dashboard
- [ ] Components
- [ ] API Integration

## ✅ Fase 7 (Semana 3): COMPLIANCE & SECURITY
- [ ] Compliance Manager
- [ ] Authentication
- [ ] API Keys

## ✅ Fase 8 (Semana 3-4): TESTING & DEPLOYMENT
- [ ] Unit tests
- [ ] Docker
- [ ] CI/CD

## ✅ Fase 9 (Semana 4+): MONITORING
- [ ] Prometheus
- [ ] Grafana
- [ ] Performance tuning

## ✅ Fase 10: LAUNCH
- [ ] Pre-launch checklist
- [ ] Production deployment
- [ ] Post-launch support

---

**Total Estimado:** 4-6 semanas para MVP completo  
**Linguagem:** Python 3.11 + FastAPI + React  
**Database:** PostgreSQL + Redis  
**Hospedagem:** AWS (EC2 + RDS + ElastiCache)  
**Custo:** ~$50/mês infraestrutura

**Pronto para começar? Use cada PROMPT sequencialmente no seu editor de código!**