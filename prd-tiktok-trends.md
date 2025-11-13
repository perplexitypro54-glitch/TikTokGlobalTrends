# 📋 PRD - TikTok Global Trends Monitoring System

**Versão:** 2.0  
**Data:** Novembro 2025  
**Status:** Ready for Development  

---

## 1. VISÃO DO PRODUTO

### 1.1 Objetivo Principal
Criar um **sistema automático de monitoramento de tendências globais do TikTok** que coleta, processa e classifica trends em tempo real de 15+ países, priorizando API Oficial para máxima conformidade legal e segurança.

### 1.2 Problema Resolvido
- ❌ Ferramentas existentes custam $1,000-5,000/mês
- ❌ Scraping agressivo leva a bloqueios
- ❌ Sem suporte multi-país/multi-nicho
- ❌ Sem conformidade legal (LGPD/GDPR/CCPA)

✅ **Solução:** Sistema API-First, zero custo, 15+ países, conformidade garantida

### 1.3 Público-Alvo
- Agências de marketing digital
- Criadores de conteúdo
- Pesquisadores de mercado
- Empresas de e-commerce
- Produtoras de vídeo

---

## 2. ESCOPO DO PRODUTO

### 2.1 MVP (Fase 1)
**Países:** USA, Brasil  
**Dados:** Hashtags, Sons, Criadores em alta  
**Frequência:** 4x por dia  
**Nichos:** 15 principais (BookTok, FitTok, FoodTok, etc)  
**Saída:** CSV, JSON, API REST  

### 2.2 Fase 2 (Semanas 5-8)
**Países adicionais:** 5 (Indonésia, México, Filipinas, Vietnã, Egito)  
**Dashboard:** Web UI básico  
**Alertas:** Notificações de trends emergentes  
**Analytics:** Gráficos de crescimento  

### 2.3 Fase 3 (Semanas 9-12)
**Países:** 15 total  
**ML:** Previsão de trends  
**Análise de Sentimento:** Comentários  
**Integrações:** Slack, Telegram, Discord  

### 2.4 Fora de Escopo
- ❌ Gerenciamento de contas TikTok
- ❌ Agendamento de posts
- ❌ Analytics de usuários específicos (privacidade)
- ❌ Recomendações de hashtags customizadas (v1)

---

## 3. ARQUITETURA DE FUNCIONALIDADES

### 3.1 Core Features

#### 3.1.1 Coleta de Dados (Data Collection)
```
Responsabilidade: Buscar dados de 3 fontes
Entrada: Configuração por país (country_code, niches)
Saída: Raw data JSON
Frequência: 4-6x por dia por país
Fonte 1: TikTok Official API
  - Query de hashtags em alta
  - Informações de vídeos
  - Métricas de engajamento
  - Rate Limit: 600 req/min

Fonte 2: Creative Center Web Scraper
  - Parse de trends principais
  - Validação de dados
  - Interface multilíngue

Fonte 3: Fallback Playwright
  - Vídeos virais específicos
  - Dados complementares
  - Usado se Fonte 1/2 insuficiente
```

#### 3.1.2 Processamento de Dados (Data Processing)
```
Responsabilidade: Limpar, normalizar, classificar
Entrada: Raw data de coleta
Saída: Structured data
Processos:
  1. Limpeza: Remove duplicatas, dados nulos
  2. Normalização: Padrões de formato, encoding
  3. Classificação: Por nicho (BookTok, FitTok, etc)
  4. Enriquecimento: Detecta tendências emergentes
  5. Armazenamento: Salva em DB + Redis cache
```

#### 3.1.3 Orquestração Multi-País (Orchestration)
```
Responsabilidade: Agendar jobs por país respeitando fusos
Entrada: Lista de países, frequência, horários
Saída: Jobs executados no horário certo
Engine: APScheduler + Timezone awareness
Exemplo:
  - USA (EST): 6h, 12h, 15h, 21h
  - Brasil (BRT): 8h, 14h, 17h, 23h
  - Indonésia (WIB): 5h, 11h, 14h, 20h
```

#### 3.1.4 Filtro por Nicho (Niche Classification)
```
Responsabilidade: Classificar conteúdo em nichos
Entrada: Hashtags, títulos, descrições
Saída: Niche + confidence score
Nichos Suportados (por país):
  USA: BookTok, HealthTok, DIYTok, GamingTok, FinanceTok
  Brasil: MusicTok, ComedyTok, FinanceTok, ActivismTok, FoodTok
  Indonésia: DanceTok, BeautyTok, FashionTok, CommerceTok
  ... (customizados por país)
```

#### 3.1.5 API REST (Backend)
```
Responsabilidade: Expor dados via HTTP
Endpoints:
  GET /api/trends/{country}/{niche}
    - Retorna top 50 trends do país/nicho
    - Sortado por engagement
    - Response: JSON
  
  GET /api/countries
    - Lista países suportados
    - Response: {country: "US", users: 136M, growth: "+5%"}
  
  GET /api/niches/{country}
    - Lista nichos disponíveis para país
  
  GET /api/health
    - Status do sistema
    - Última execução por país
    - Erros recentes
  
  POST /api/export/{country}/{niche}
    - Exporta trends em CSV
    - Parâmetros: date_range, format
  
  GET /api/analytics
    - Estatísticas agregadas
    - Gráficos de crescimento
```

#### 3.1.6 Dashboard Web (Frontend)
```
Responsabilidade: Visualizar dados em tempo real
Componentes:
  1. Seletor de País
     - Dropdown com 15 países
     - Shows: Users (M), Growth (%), Última atualização
  
  2. Seletor de Nicho
     - Dinâmico baseado no país
     - Shows: # de trends, trending up/down
  
  3. Tabela de Trends
     - Top 50 hashtags/sons/criadores
     - Colunas: Rank, Name, Posts, Views, Growth
     - Sorting: Por engagement/crescimento/data
  
  4. Gráficos
     - Line chart: Evolução de top 5 trends (7 dias)
     - Bar chart: Comparação entre países
     - Heatmap: Nichos por país (quente/frio)
  
  5. Export
     - Download CSV de trend selecionado
     - Agendamento de relatórios via email
```

#### 3.1.7 Conformidade Legal (Compliance)
```
Responsabilidade: Garantir conformidade regional
Por Região:
  LGPD (Brasil):
    - Consentimento explícito
    - Retenção máxima: 365 dias
    - Direito de delete implementado
    - Finalidade específica documentada
  
  GDPR (Europa):
    - Consentimento duplo (opt-in + opt-in)
    - DPA assinado
    - Dados residentes em EU
    - Retenção máxima: 90 dias
    - Right to be forgotten automatizado
  
  CCPA (USA):
    - Transparência clara
    - Opt-out disponível
    - Delete on request <45 dias
    - Disclosure de coleta
  
  PDPA (Ásia):
    - Dados localizados no país
    - Conformidade com leis locais
    - Notificação de violações em 72h
```

---

## 4. FLUXO DE DADOS

### 4.1 Happy Path
```
1. Scheduler dispara job para país X
   ↓
2. API Client autentica com TikTok
   ↓
3. Query de hashtags/sons/criadores em alta
   ↓
4. Creative Center scraper valida dados (paralelo)
   ↓
5. Dados processados e classificados por nicho
   ↓
6. Salvos em PostgreSQL + Redis cache
   ↓
7. Webhook notifica dashboard
   ↓
8. API expõe dados para consulta
```

### 4.2 Fallback Path
```
Se API falhar:
1. Tenta Creative Center Scraper
   ↓
2. Se CC também falhar, usa Playwright
   ↓
3. Se tudo falhar, usa cached data anterior
   ↓
4. Log de erro enviado para Sentry
   ↓
5. Admin notificado via Slack
```

---

## 5. REQUISITOS NÃO-FUNCIONAIS

### 5.1 Performance
- **Latência:** <2 segundos por query
- **Throughput:** 15+ países × 4 execuções/dia = 60 jobs/dia
- **Uptime:** 99.9%
- **Taxa de erro:** <5%

### 5.2 Segurança
- HTTPS/TLS obrigatório
- API key rotation automática
- Rate limiting (100 req/min por IP)
- Input validation em todos endpoints
- SQL injection prevention (prepared statements)
- CORS configurado corretamente

### 5.3 Escalabilidade
- Suporta crescimento de 2 para 100+ países
- Microsserviços desacoplados
- Banco de dados particionado por país
- Cache distribuído com Redis
- Load balancing com Nginx

### 5.4 Confiabilidade
- Retry automático com exponential backoff
- Circuit breaker pattern
- Dead letter queue para falhas
- Health checks a cada 5 minutos
- Backups diários do banco de dados

### 5.5 Manutenibilidade
- Código modular e bem documentado
- Testes de cobertura >80%
- CI/CD automatizado
- Logging estruturado (JSON)
- Documentação de API com Swagger

---

## 6. MODELOS DE DADOS

### 6.1 Core Models

```
Hashtag
  id: UUID
  name: String (e.g., "#booktok")
  country: String (e.g., "US")
  niche: String (e.g., "booktok")
  posts_count: Int
  views_count: Int
  engagement_rate: Float
  growth_rate: Float (%)
  trend_direction: Enum (UP, DOWN, STABLE)
  rank: Int (posição no ranking)
  created_at: DateTime
  updated_at: DateTime
  last_scraped_at: DateTime

Video
  id: UUID
  tiktok_video_id: String (ID do TikTok)
  hashtags: [String]
  niches: [String]
  views: Int
  likes: Int
  comments: Int
  shares: Int
  engagement_rate: Float
  creator_id: String
  created_at: DateTime
  country: String
  viral_score: Float (0-100)

Creator
  id: UUID
  tiktok_creator_id: String
  username: String
  followers: Int
  follower_growth: Float
  niches: [String]
  country: String
  is_trending: Boolean
  rank: Int
  created_at: DateTime
  updated_at: DateTime

Sound
  id: UUID
  tiktok_sound_id: String
  name: String
  artist: String
  usage_count: Int
  growth_rate: Float
  country: String
  niches: [String]
  rank: Int
  created_at: DateTime

Trend
  id: UUID
  name: String (e.g., "BookTok Summer 2025")
  country: String
  niche: String
  hashtags: [String]
  sounds: [String]
  creators: [String]
  start_date: DateTime
  end_date: DateTime (NULL = ongoing)
  viral_score: Float
  sentiment: Enum (POSITIVE, NEGATIVE, NEUTRAL)
  created_at: DateTime

User (Admin)
  id: UUID
  email: String
  password_hash: String
  role: Enum (ADMIN, VIEWER)
  preferences: JSON (countries, niches, notification_settings)
  created_at: DateTime

ApiKey
  id: UUID
  key: String (hashed)
  user_id: UUID
  country_access: [String] (quais países pode acessar)
  rate_limit: Int (req/min)
  created_at: DateTime
  expires_at: DateTime
```

---

## 7. REQUISITOS TÉCNICOS

### 7.1 Stack Recomendado
- **Linguagem:** Python 3.11+
- **Backend Framework:** FastAPI
- **Async:** AsyncIO + AIOHTTP
- **Database:** PostgreSQL 15+
- **Cache:** Redis 7+
- **Task Queue:** Celery (opcional, Phase 3)
- **Scheduler:** APScheduler
- **Scraping:** Playwright + BeautifulSoup4
- **ORM:** SQLAlchemy 2.0
- **Frontend:** React 18 + TypeScript
- **Containerization:** Docker + Docker Compose
- **Orchestration:** Kubernetes (v1.27+)

### 7.2 Infraestrutura
- **Cloud:** AWS (ou GCP/Azure)
- **Compute:** EC2 t3.medium (~$30/mês)
- **Database:** RDS PostgreSQL db.t3.micro (~$15/mês)
- **Cache:** ElastiCache Redis cache.t3.micro (~$5/mês)
- **Storage:** S3 (~$1/mês)
- **CDN:** CloudFront (opcional)
- **Total mensal:** ~$50

### 7.3 Dependências Python (requirements.txt)
```
fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
playwright==1.41.0
beautifulsoup4==4.12.2
requests==2.31.0
httpx==0.25.2
pandas==2.1.3
aiohttp==3.9.1
apscheduler==3.10.4
pydantic==2.5.0
python-dotenv==1.0.0
pyjwt==2.8.1
passlib==1.7.4
sentry-sdk==1.38.0
prometheus-client==0.19.0
```

---

## 8. FASES DE DESENVOLVIMENTO

### Fase 1: MVP (Semanas 1-2)
**Objetivo:** USA + Brasil operacionais
- Database schema
- API Client TikTok
- Creative Center Scraper
- Processamento básico
- Armazenamento em DB
- **Saída:** Dados coletados funcionando

### Fase 2: Expansão Regional (Semanas 3-4)
**Objetivo:** 5 países adicionais
- Suporte multi-país
- Nichos customizados
- Dashboard básico
- **Saída:** 7 países monitorados

### Fase 3: Conformidade & Segurança (Semana 5)
**Objetivo:** Pronto para produção
- LGPD/GDPR/CCPA implementados
- Security hardening
- Testes de penetração
- **Saída:** Compliance 100%

### Fase 4: Otimizações (Semanas 6+)
**Objetivo:** Scale and Advanced Features
- ML para previsão
- Análise de sentimento
- Integrações (Slack, etc)
- **Saída:** Sistema de classe mundial

---

## 9. CRITÉRIOS DE SUCESSO

### MVP (Fase 1)
- ✅ Coleta de 100+ hashtags por país
- ✅ 4 execuções/dia sem erros
- ✅ Dados estruturados em PostgreSQL
- ✅ API REST respondendo com <2s latência
- ✅ <5% taxa de erro

### Fase 2
- ✅ 7 países sincronizados
- ✅ Dashboard web funcionando
- ✅ 50+ nichos suportados
- ✅ Alertas de trends emergentes

### Fase 3
- ✅ 100% conformidade legal verificada
- ✅ Uptime 99.9% em produção
- ✅ Zero bloqueios por TikTok
- ✅ Testes de penetração aprovados

---

## 10. DEPENDÊNCIAS & RISCOS

### 10.1 Dependências Externas
- Aprovação da TikTok Developer Platform (24-48h)
- Disponibilidade API TikTok (SLA deles)
- Infraestrutura AWS funcional
- Internet connection estável

### 10.2 Riscos Técnicos
| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|--------|-----------|
| API TikTok muda | Média | Alto | Fallback Creative Center |
| Rate limit excedido | Baixa | Médio | Implementar backoff |
| BD cai | Baixa | Alto | Backups diários |
| Scraper quebra | Média | Médio | Manutenção regular |

---

## 11. ROADMAP PÓS-LAUNCH

### Q1 2026
- [ ] Machine Learning para previsão de trends
- [ ] Análise de sentimento em comentários
- [ ] Integração com Shopify/WooCommerce

### Q2 2026
- [ ] Mobile app (iOS + Android)
- [ ] Suporte para 50+ países
- [ ] API pública (SaaS)

### Q3 2026
- [ ] Recomendações de conteúdo
- [ ] Geração de relatórios automáticos
- [ ] Integração com TikTok Ads

---

## 12. DEFINIÇÕES

- **Trend:** Um tópico/hashtag que está crescendo em popularidade
- **Nicho:** Categoria de conteúdo (e.g., BookTok, FitTok)
- **Engajamento:** (likes + comments + shares) / total_viewers
- **Viral Score:** 0-100 calculado por engagement_rate + growth_rate
- **Rate Limit:** Máximo de requisições por minuto à API

---

**PRD Finalizado e Pronto para Desenvolvimento**