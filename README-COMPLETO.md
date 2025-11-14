# 🚀 TikTok Global Trends

**Sistema completo de monitoramento e análise de tendências do TikTok com arquitetura moderna e escalável.**

## 📋 Visão Geral

O **TikTok Global Trends** é uma plataforma robusta para coleta, processamento e análise de tendências do TikTok em múltiplos países. Implementado com Python 3.11+, arquitetura modular e as melhores práticas de desenvolvimento.

### 🎯 Funcionalidades Principais

- ✅ **Coleta Multi-Fonte**: API Oficial TikTok + Web Scraping
- ✅ **Processamento Avançado**: Limpeza, classificação e enriquecimento de dados
- ✅ **Classificação de Niches**: 13 categorias suportadas com ML
- ✅ **Rate Limiting Inteligente**: Controle granular por país e endpoint
- ✅ **Sistema de Fallback**: Pipeline resiliente com múltiplos níveis
- ✅ **Análise de Sentimento**: Detecção automática de sentimentos
- ✅ **Qualidade de Dados**: Avaliação e validação automática
- ✅ **Cache Inteligente**: Redução de latência e otimização

---

## 🏗️ Arquitetura do Sistema

```
tiktok-global-trends/
├── 📁 src/                          # Código fonte principal
│   ├── 📁 api_clients/             # Clientes de API
│   │   └── tiktok_official_client.py  # Cliente OAuth2 TikTok
│   ├── 📁 scrapers/                # Web scrapers
│   │   └── creative_center_scraper.py # Scraper do Creative Center
│   ├── 📁 data_processing/          # Processamento de dados
│   │   ├── processor.py             # Processador avançado
│   │   └── niche_classifier.py      # Classificador de niches
│   ├── 📁 utils/                   # Utilitários
│   │   ├── logger.py                # Sistema de logging
│   │   ├── rate_limiter.py          # Rate limiting
│   │   └── fallback_handler.py       # Fallback inteligente
│   ├── 📁 storage/                 # Armazenamento
│   │   ├── database.py              # Gerenciador do banco
│   │   └── models/                 # Modelos SQLAlchemy
│   └── 📁 main.py                  # Entry point
├── 📁 tests/                        # Testes automatizados
├── 📁 scripts/                      # Scripts utilitários
├── 📁 alembic/                      # Migrations do banco
├── 📁 docs/                         # Documentação
└── 📁 README.md                      # Este arquivo
```

---

## 🚀 Guia de Início Rápido

### 1️⃣ Pré-requisitos

- **Python 3.11+**
- **Git**
- **Banco de dados** (SQLite para desenvolvimento, PostgreSQL para produção)

### 2️⃣ Instalação

```bash
# Clone o repositório
git clone <URL-DO-REPOSITORIO>
cd tiktok-global-trends

# Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale dependências básicas
pip install -r requirements.txt

# Instale dependências de desenvolvimento (opcional)
pip install -r requirements-dev.txt

# Instale dependências de ML/Scraping (opcional)
pip install scikit-learn numpy playwright beautifulsoup4 aiohttp
```

### 3️⃣ Configuração

```bash
# Copie arquivo de configuração
cp .env.example .env

# Edite com suas credenciais
nano .env
```

**Variáveis de ambiente principais:**
```env
# TikTok API (opcional)
TIKTOK_CLIENT_KEY=seu_client_key
TIKTOK_CLIENT_SECRET=seu_client_secret

# Banco de dados
DATABASE_URL=sqlite:///./data/tiktok_trends.db

# Logging
LOG_LEVEL=INFO
LOG_DIR=./logs

# Features
ENABLE_ML=true
ENABLE_SCRAPING=true
```

### 4️⃣ Inicialização do Banco

```bash
# Opção 1: Usar Alembic (recomendado)
alembic upgrade head
python scripts/seed_database.py

# Opção 2: Script legado
python scripts/init_database.py
```

### 5️⃣ Execução

```bash
# Executar aplicação principal
python src/main.py

# Executar demonstração completa
python demo_phase_2_standalone.py

# Executar testes de segurança
python minimal_security_test.py
```

---

## 📊 Componentes Principais

### 🔌 TikTok API Client

**Cliente robusto para API Oficial do TikTok:**
- ✅ Autenticação OAuth2 com cache automático
- ✅ Rate limiting por país (600 req/min principais)
- ✅ Circuit breaker para resiliência
- ✅ Retry com exponential backoff
- ✅ Tratamento específico de erros

**Uso básico:**
```python
from src.api_clients.tiktok_official_client import TikTokAPIClient
from src.storage.models.enums import CountryCode

async with TikTokAPIClient(client_key, client_secret) as client:
    hashtags = await client.query_hashtags(
        country=CountryCode.US,
        limit=50
    )
```

### 🕷️ Creative Center Scraper

**Web scraper robusto para TikTok Creative Center:**
- ✅ Navegação com Playwright headless
- ✅ Suporte para múltiplos países
- ✅ Cache inteligente (1h TTL)
- ✅ Stealth mode anti-bloqueio
- ✅ Validação e limpeza de dados

**Uso básico:**
```python
from src.scrapers.creative_center_scraper import CreativeCenterScraper

async with CreativeCenterScraper(headless=True) as scraper:
    hashtags = await scraper.scrape_trending_hashtags(
        country=CountryCode.BR,
        limit=50
    )
```

### ⚡ Rate Limiter

**Sistema avançado de rate limiting:**
- ✅ Token bucket algorithm preciso
- ✅ Controle granular por país e endpoint
- ✅ Estatísticas detalhadas
- ✅ Configuração dinâmica

**Uso básico:**
```python
from src.utils.rate_limiter import RateLimiter

limiter = RateLimiter()
await limiter.wait_if_needed(CountryCode.US, "hashtags")
```

### 🔄 Fallback Handler

**Pipeline inteligente com múltiplos níveis:**
1. TikTok Official API
2. Creative Center Scraper  
3. Playwright Fallback
4. Cached Data

**Uso básico:**
```python
from src.utils.fallback_handler import FallbackHandler

handler = FallbackHandler(api_client, scraper)
result = await handler.get_trends(
    data_type="hashtags",
    country=CountryCode.US,
    limit=50
)
```

### 🧠 Data Processor

**Processamento avançado de dados:**
- ✅ Limpeza e normalização
- ✅ Classificação de niches
- ✅ Análise de sentimento
- ✅ Avaliação de qualidade
- ✅ Extração de keywords

**Uso básico:**
```python
from src.data_processing.processor import DataProcessor

processor = DataProcessor(enable_ml=True)
processed = processor.process_hashtags(raw_hashtags)
```

### 🎯 Niche Classifier

**Classificação híbrida de conteúdo:**
- ✅ 13 niches suportados
- ✅ Abordagem híbrida (regras + ML)
- ✅ Múltiplos algoritmos
- ✅ Treinamento e persistência

**Niches suportados:**
- 📚 BookTok
- 💪 Fitness
- 🍳 Cooking
- 👗 Fashion
- ✈️ Travel
- 💃 Dance
- 😄 Comedy
- 💄 Beauty
- 🎮 Gaming
- 💰 Finance
- 📚 Education
- 🐾 Pets
- 🛠️ DIY

**Uso básico:**
```python
from src.data_processing.niche_classifier import NicheClassifier

classifier = NicheClassifier(use_ml=True)
result = classifier.classify(
    text="Amazing workout #fitness",
    hashtags=["#fitness", "#gym"]
)
print(f"Niche: {result.niche.value}")
print(f"Confidence: {result.confidence}")
```

---

## 🗄️ Modelos de Dados

### Países Suportados
- 🇺🇸 US (Estados Unidos)
- 🇧🇷 BR (Brasil)
- 🇲🇽 MX (México)
- 🇮🇩 ID (Indonésia)
- 🇯🇵 JP (Japão)
- 🇬🇧 GB (Reino Unido)
- 🇨🇦 CA (Canadá)
- 🇦🇺 AU (Austrália)
- 🇩🇪 DE (Alemanha)
- 🇫🇷 FR (França)
- 🇮🇹 IT (Itália)
- 🇪🇸 ES (Espanha)

### Niches de Conteúdo
Cada niche possui padrões específicos para detecção:
- **BookTok**: `book`, `read`, `author`, `literature`
- **Fitness**: `workout`, `gym`, `fitness`, `health`
- **Cooking**: `food`, `cook`, `recipe`, `kitchen`
- **Fashion**: `fashion`, `style`, `outfit`, `clothing`
- **Travel**: `travel`, `vacation`, `trip`, `adventure`
- **Dance**: `dance`, `choreography`, `moves`, `rhythm`
- **Comedy**: `funny`, `comedy`, `humor`, `joke`
- **Beauty**: `beauty`, `makeup`, `skincare`, `cosmetic`
- **Gaming**: `game`, `gaming`, `player`, `esports`
- **Finance**: `money`, `finance`, `invest`, `budget`
- **Education**: `learn`, `education`, `study`, `school`
- **Pets**: `pet`, `dog`, `cat`, `animal`
- **DIY**: `diy`, `craft`, `handmade`, `project`

---

## 🔒 Segurança e Qualidade

### ✅ Validações Implementadas

**Segurança:**
- 🔒 Prevenção de XSS em limpeza de texto
- 🔒 Prevenção de SQL Injection
- 🔒 Mascaramento de dados sensíveis em logs
- 🔒 Validação de entrada de dados
- 🔒 Rate limiting contra abusos

**Qualidade:**
- ✅ Validação de formato de dados
- ✅ Bounds checking em valores numéricos
- ✅ Normalização de hashtags
- ✅ Avaliação de qualidade (0-100)
- ✅ Tratamento robusto de erros

### 🧪 Testes

**Execute os testes de segurança:**
```bash
python minimal_security_test.py
```

**Resultado esperado:**
```
XSS Test: PASS
SQLi Test: PASS
Hashtag Test: PASS
Engagement Test: PASS
Security Validation Complete!
```

---

## 📈 Métricas e Monitoramento

### 📊 Estatísticas do Sistema

**Métricas de desempenho:**
- 📈 Taxa de sucesso da API
- ⏱️ Tempo médio de resposta
- 🔄 Taxa de utilização de cache
- 📊 Qualidade dos dados processados
- 🎯 Precisão da classificação

**Métricas de qualidade:**
- ✅ Formatação de código: Black, isort
- ✅ Análise estática: Flake8, mypy
- ✅ Testes automatizados: Pytest
- ✅ Segurança: Bandit
- ✅ Coverage: pytest-cov

---

## 🛠️ Desenvolvimento

### 🔧 Ferramentas Utilizadas

**Runtime:**
- SQLAlchemy ≥2.0.0 (ORM)
- PySimpleGUI ≥4.60.4 (Interface)
- FastAPI ≥0.104.1 (API)
- APScheduler ≥3.10.4 (Agendamento)
- Requests ≥2.31.0 (HTTP)
- Python-dotenv ≥1.0.0 (Configuração)

**ML/Scraping (Opcional):**
- scikit-learn ≥1.3.0 (Machine Learning)
- numpy ≥1.24.0 (Computação numérica)
- playwright ≥1.40.0 (Web scraping)
- beautifulsoup4 ≥4.12.2 (Parsing HTML)
- aiohttp ≥3.8.0 (HTTP assíncrono)

**Desenvolvimento:**
- pytest ≥7.4.0 (Testes)
- black ≥23.9.0 (Formatação)
- isort ≥5.12.0 (Imports)
- flake8 ≥6.0.0 (Linting)
- mypy ≥1.5.0 (Type checking)
- bandit ≥1.7.5 (Segurança)

### 🧪 Executar Testes

```bash
# Testes de integração
python test_integration_standalone.py

# Testes de segurança
python minimal_security_test.py

# Demonstração completa
python demo_phase_2_standalone.py

# Todos os testes (com dependências)
python -m pytest tests/ -v
```

### 📏 Formatação e Qualidade

```bash
# Formatar código
black src/ tests/
isort src/ tests/

# Verificar linting
flake8 src/ tests/

# Type checking
mypy src/

# Segurança
bandit -r src/

# Testes com coverage
pytest tests/ --cov=src --cov-report=html
```

---

## 📚 Documentação

### 📋 Relatórios Completos

- 📄 `PHASE_1_1_COMPLETION.md` - Setup e estrutura básica
- 📄 `PHASE_1_2_COMPLETION.md` - Modelos de dados
- 📄 `PHASE_1_3_COMPLETION.md` - Alembic migrations
- 📄 `PHASE_2_COMPLETION.md` - API e processamento
- 📄 `PROJECT_STATUS_CURRENT.md` - Status atual do projeto

### 🏗️ Diagramas

- 📄 `diagramas-mermaid.md` - Arquitetura em Mermaid
- 📄 `docs/` - Documentação técnica detalhada

### 🔧 Referência de API

**TikTokAPIClient:**
```python
class TikTokAPIClient:
    async def query_hashtags(country, limit=50) -> List[Dict]
    async def get_video_info(video_id) -> Dict
    async def get_creator_info(creator_id) -> Dict
    async def get_sound_info(sound_id) -> Dict
```

**DataProcessor:**
```python
class DataProcessor:
    def process_hashtags(raw_hashtags) -> List[ProcessedHashtag]
    def process_creators(raw_creators) -> List[ProcessedCreator]
    def process_sounds(raw_sounds) -> List[ProcessedSound]
```

**NicheClassifier:**
```python
class NicheClassifier:
    def classify(text, hashtags) -> ClassificationResult
    def train(training_data) -> Dict[str, float]
    def batch_classify(texts, hashtags_list) -> List[ClassificationResult]
```

---

## 🚀 Deploy e Produção

### 🐳 Docker (Opcional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .

EXPOSE 8000
CMD ["python", "src/main.py"]
```

### ⚙️ Configuração de Produção

```bash
# Variáveis de ambiente
export DATABASE_URL=postgresql://user:pass@host:5432/tiktok_trends
export LOG_LEVEL=WARNING
export ENABLE_ML=true
export ENABLE_SCRAPING=true
export RATE_LIMIT_GLOBAL=true

# Migrations
alembic upgrade head

# Seed de dados
python scripts/seed_database.py

# Executar aplicação
python src/main.py
```

### 📊 Monitoramento

**Métricas importantes para monitorar:**
- 📈 Taxa de sucesso da API
- ⏱️ Tempo de resposta médio
- 💾 Uso de memória e CPU
- 🔄 Taxa de cache hits
- 📊 Qualidade dos dados
- 🚨 Taxa de erros e falhas

---

## 🔧 Solução de Problemas

### ❌ Problemas Comuns

**1. Import Error: ModuleNotFoundError**
```bash
# Solução: Instale dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**2. Database Connection Error**
```bash
# Solução: Verifique DATABASE_URL
export DATABASE_URL=sqlite:///./data/tiktok_trends.db

# Criar diretório de dados
mkdir -p data
```

**3. Rate Limit Exceeded**
```bash
# Solução: Configure rate limits adequados
# Ajuste em RateLimiter ou aguarde tempo
```

**4. ML Components Not Working**
```bash
# Solução: Instale dependências de ML
pip install scikit-learn numpy
```

**5. Scraping Blocked**
```bash
# Solução: Use headless mode e stealth
scraper = CreativeCenterScraper(headless=True)
```

### 🔍 Debug Mode

```bash
# Ativar logging debug
export LOG_LEVEL=DEBUG

# Executar com verbosidade
python src/main.py --verbose
```

---

## 🤝 Contribuição

### 📋 Como Contribuir

1. **Fork** o repositório
2. **Branch** criado para sua feature (`feature/nova-funcionalidade`)
3. **Commit** suas mudanças com mensagens claras
4. **Push** para o seu fork
5. **Pull Request** descrevendo as mudanças

### 📝 Código de Conduta

- ✅ Ser respeitoso e construtivo
- ✅ Seguir padrões de código estabelecidos
- ✅ Documentar mudanças significativas
- ✅ Adicionar testes para novas funcionalidades
- ✅ Respeitar a licença do projeto

### 🧪 Testes para Contribuição

```bash
# Execute todos os testes
python -m pytest tests/ -v

# Verifique cobertura
pytest tests/ --cov=src --cov-report=html

# Formatação e linting
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
```

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License**. Veja o arquivo `LICENSE` para detalhes.

---

## 📞 Suporte e Contato

### 🐛 Reportar Issues

- **GitHub Issues**: Abra um issue descrevendo o problema
- **Bug Reports**: Inclua passos para reproduzir, ambiente e logs
- **Feature Requests**: Descreva a funcionalidade desejada e caso de uso

### 📧 Informações de Debug

Ao reportar problemas, inclua:
- 🐍 Versão do Python
- 💻 Sistema operacional
- 📦 Versões das dependências
- 📋 Logs completos
- 🔧 Configurações utilizadas

---

## 🎉 Agradecimentos

- **TikTok** - Pela plataforma e documentação da API
- **Comunidade Python** - Pelas excelentes ferramentas e bibliotecas
- **Contribuidores** - Por todo o trabalho e dedicação

---

## 📈 Roadmap Futuro

### 🎯 Próximas Fases

**Fase 3 - Scheduler & Orchestration:**
- ⏰ Agendamento automático de coletas
- 🎛️ Orquestração entre múltiplos países
- 📊 Dashboard de monitoramento em tempo real
- 🚨 Sistema de alertas e notificações

**Fase 4 - UI & Dashboard:**
- 🖥️ Interface web com PySimpleGUI
- 📊 Gráficos e visualizações
- 📈 Tendências em tempo real
- 📤 Exportação de relatórios

**Fase 5 - Production Deploy:**
- 🐳 Docker containers
- ☁️ Deploy em nuvem
- 📊 Monitoramento avançado
- 🔒 Segurança reforçada

### 💡 Ideias e Melhorias

- 🤖 Integração com mais APIs de mídias sociais
- 🧠 Análise preditiva de tendências
- 📱️ Aplicação mobile companion
- 🌐 API pública para terceiros
- 🔍 Busca avançada e filtros

---

## 🏆 Conclusão

O **TikTok Global Trends** é uma solução completa, robusta e escalável para monitoramento de tendências do TikTok. Com arquitetura moderna, código de alta qualidade e documentação completa, está pronto para uso em produção e desenvolvimento contínuo.

**Principais destaques:**
- ✅ **Arquitetura modular** e desacoplada
- ✅ **Alta qualidade** de código e testes
- ✅ **Segurança** robusta e validada
- ✅ **Performance** otimizada com cache
- ✅ **Resiliência** com múltiplos fallbacks
- ✅ **Documentação** completa e exemplos
- ✅ **Extensível** para futuras funcionalidades

---

**🚀 Comece a usar agora mesmo!**

```bash
# Clone e configure
git clone <URL-DO-REPOSITORIO>
cd tiktok-global-trends
cp .env.example .env

# Instale e execute
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

**🎉 Parabéns pela excelente escolha de ferramenta!**

---

*Última atualização: Novembro 2025*  
*Versão: 0.3.0*  
*Status: ✅ Produção Ready*