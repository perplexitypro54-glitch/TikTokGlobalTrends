// mermaid-architecture.md - Diagramas da Arquitetura do Projeto

# 🎨 DIAGRAMAS MERMAID - TikTok Global Trends v2.0

## 1. ARQUITETURA DE SISTEMA (Visão Geral)

```mermaid
graph TB
    subgraph "Data Sources"
        API["🔗 TikTok Official API<br/>Rate: 600 req/min"]
        CC["🌐 Creative Center<br/>Web Interface"]
        PW["🤖 Playwright Scraper<br/>Fallback"]
    end

    subgraph "Orchestration"
        SCHED["⏰ APScheduler<br/>15+ Países<br/>Timezone-aware"]
        MONITOR["📊 Health Monitor<br/>Alertas"]
    end

    subgraph "Processing Pipeline"
        COLLECT["1️⃣ Coleta<br/>Raw Data"]
        CLEAN["2️⃣ Limpeza<br/>Remove dups"]
        NORM["3️⃣ Normalização<br/>Padrões"]
        CLASS["4️⃣ Classificação<br/>Nichos"]
        ENRICH["5️⃣ Enriquecimento<br/>Scores"]
    end

    subgraph "Storage"
        DB["🗄️ PostgreSQL<br/>Dados Principais"]
        REDIS["⚡ Redis<br/>Cache"]
        S3["📦 S3<br/>Arquivos"]
    end

    subgraph "API & Frontend"
        RESTAPI["🔌 FastAPI REST<br/>GET /trends/{country}"]
        DASH["🎨 Dashboard Web<br/>React + TS"]
        EXPORT["📥 Export Service<br/>CSV/JSON"]
    end

    subgraph "Monitoring & Compliance"
        PROM["📈 Prometheus<br/>Métricas"]
        SENTRY["🚨 Sentry<br/>Error Tracking"]
        AUDIT["✅ Audit Log<br/>LGPD/GDPR"]
    end

    API --> SCHED
    CC --> SCHED
    PW --> SCHED
    SCHED --> COLLECT
    MONITOR --> SCHED
    
    COLLECT --> CLEAN
    CLEAN --> NORM
    NORM --> CLASS
    CLASS --> ENRICH
    
    ENRICH --> DB
    ENRICH --> REDIS
    ENRICH --> S3
    
    DB --> RESTAPI
    REDIS --> RESTAPI
    RESTAPI --> DASH
    RESTAPI --> EXPORT
    
    RESTAPI --> PROM
    COLLECT --> SENTRY
    ENRICH --> AUDIT
```

## 2. FLUXO DE DADOS - HAPPY PATH

```mermaid
sequenceDiagram
    participant SCHED as Scheduler
    participant API as TikTok API
    participant CC as Creative Center
    participant PROC as Processor
    participant DB as PostgreSQL
    participant REDIS as Redis
    participant REST as REST API
    
    SCHED->>API: 1. Query trends (USA, 4x/dia)
    API-->>SCHED: Hashtags JSON
    
    SCHED->>CC: 2. Scrape trends (validação)
    CC-->>SCHED: Trends HTML
    
    SCHED->>PROC: 3. Enviar raw data
    PROC->>PROC: Limpar + Normalizar
    PROC->>PROC: Classificar nicho
    PROC->>PROC: Calcular scores
    
    PROC->>DB: 4. Salvar trends
    PROC->>REDIS: 5. Cache (TTL 1h)
    
    REST->>DB: 6. Query trends (user request)
    REST-->>REDIS: Check cache
    REDIS-->>REST: Cache hit!
    REST-->>User: JSON response <2s
```

## 3. FLUXO DE DADOS - FALLBACK PATH

```mermaid
sequenceDiagram
    participant SCHED as Scheduler
    participant API as TikTok API
    participant CC as Creative Center
    participant PW as Playwright
    participant CACHE as Cache
    participant ALERT as Alert System
    
    SCHED->>API: 1. Query trends
    API-->>SCHED: ❌ Rate limit exceeded
    
    SCHED->>CC: 2. Fallback Creative Center
    CC-->>SCHED: ❌ Scraper timeout
    
    SCHED->>PW: 3. Fallback Playwright
    PW-->>SCHED: ✅ Dados obtidos (lento)
    
    SCHED->>CACHE: 4. Se tudo falhar, use cached
    CACHE-->>SCHED: ✅ Dados anteriores
    
    SCHED->>ALERT: 5. Log de erro
    ALERT->>Admin: 🚨 Email: "Coleta falhou para USA"
```

## 4. MODELO DE DADOS - RELACIONAMENTOS

```mermaid
erDiagram
    COUNTRY ||--o{ HASHTAG : has
    COUNTRY ||--o{ VIDEO : has
    COUNTRY ||--o{ CREATOR : has
    COUNTRY ||--o{ SOUND : has
    COUNTRY ||--o{ TREND : has
    
    CREATOR ||--o{ VIDEO : creates
    CREATOR ||--o{ TREND : part_of
    
    HASHTAG ||--o{ VIDEO : tags
    HASHTAG ||--o{ TREND : contains
    
    SOUND ||--o{ VIDEO : uses
    SOUND ||--o{ TREND : associated
    
    TREND ||--o{ VIDEO : aggregates
    
    USER ||--o{ APIKEY : owns
    USER ||--o{ AUDITLOG : creates
    
    COUNTRY {
        string code PK
        string name
        float usersInMillions
        float growthRate
        string timezone
        boolean isActive
    }
    
    HASHTAG {
        string id PK
        string name
        string countryId FK
        string niche
        int postsCount
        bigint viewsCount
        float engagementRate
        float growthRate
        int viralScore
        int rank
    }
    
    VIDEO {
        string id PK
        string tiktokVideoId UK
        string creatorId FK
        string countryId FK
        bigint views
        bigint likes
        float engagementRate
        float viralScore
    }
    
    CREATOR {
        string id PK
        string tiktokCreatorId UK
        string username
        bigint followers
        string countryId FK
        boolean isTrending
    }
    
    SOUND {
        string id PK
        string tiktokSoundId UK
        string name
        string artist
        int usageCount
        string countryId FK
    }
    
    TREND {
        string id PK
        string name
        string countryId FK
        float viralScore
        datetime startDate
        datetime peakDate
        datetime endDate
        boolean isActive
    }
    
    USER {
        string id PK
        string email UK
        string passwordHash
        string role
        string[] countriesAccess
        boolean isActive
    }
    
    APIKEY {
        string id PK
        string key UK
        string userId FK
        int rateLimit
        datetime expiresAt
    }
    
    AUDITLOG {
        string id PK
        string userId FK
        string action
        string resourceType
    }
```

## 5. PIPELINE DE PROCESSAMENTO DE DADOS

```mermaid
graph LR
    subgraph Input["📥 INPUT"]
        RAW["Raw JSON<br/>from API/Scraper"]
    end
    
    subgraph Clean["🧹 CLEAN"]
        REM["Remove<br/>Duplicates"]
        NULL["Remove<br/>Nulls"]
        VALID["Validate<br/>Format"]
    end
    
    subgraph Norm["📊 NORMALIZE"]
        CASE["Lowercase<br/>Keys"]
        ENC["UTF-8<br/>Encoding"]
        TZ["Timezone<br/>Conversion"]
    end
    
    subgraph Class["🏷️ CLASSIFY"]
        KEYWORDS["Match<br/>Keywords"]
        SCORE["Confidence<br/>Score"]
        MULTI["Multi-niche<br/>Support"]
    end
    
    subgraph Enrich["✨ ENRICH"]
        CALC["Calculate<br/>Metrics"]
        TREND["Detect<br/>Trends"]
        RANK["Compute<br/>Rank"]
    end
    
    subgraph Output["📤 OUTPUT"]
        SAVE["Save to DB<br/>+ Cache"]
        NOTIFY["Notify<br/>Dashboard"]
    end
    
    RAW --> REM
    REM --> NULL
    NULL --> VALID
    VALID --> CASE
    CASE --> ENC
    ENC --> TZ
    TZ --> KEYWORDS
    KEYWORDS --> SCORE
    SCORE --> MULTI
    MULTI --> CALC
    CALC --> TREND
    TREND --> RANK
    RANK --> SAVE
    SAVE --> NOTIFY
```

## 6. ORQUESTRAÇÃO MULTI-PAÍS (SCHEDULER)

```mermaid
graph TB
    SCHED["APScheduler<br/>Timezone-Aware"]
    
    SCHED -->|4x/dia EST| USA["🇺🇸 USA<br/>6h, 12h, 15h, 21h"]
    SCHED -->|4x/dia BRT| BR["🇧🇷 Brasil<br/>8h, 14h, 17h, 23h"]
    SCHED -->|6x/dia WIB| ID["🇮🇩 Indonésia<br/>5h, 8h, 11h, 14h, 17h, 20h"]
    SCHED -->|4x/dia CST| MX["🇲🇽 México<br/>7h, 13h, 16h, 22h"]
    SCHED -->|6x/dia PH| PH["🇵🇭 Filipinas<br/>5h, 9h, 12h, 15h, 18h, 21h"]
    
    USA --> COLLECT1["Coleta USA<br/>API TikTok"]
    BR --> COLLECT2["Coleta Brasil<br/>API TikTok"]
    ID --> COLLECT3["Coleta Indonésia<br/>CC + Playwright"]
    MX --> COLLECT4["Coleta México<br/>API TikTok"]
    PH --> COLLECT5["Coleta Filipinas<br/>CC + Playwright"]
    
    COLLECT1 --> PROC["Processing Pipeline"]
    COLLECT2 --> PROC
    COLLECT3 --> PROC
    COLLECT4 --> PROC
    COLLECT5 --> PROC
    
    PROC --> DB["PostgreSQL"]
    PROC --> CACHE["Redis Cache"]
    
    DB -.->|próxima coleta| SCHED
    
    style USA fill:#ffcccc
    style BR fill:#ffcccc
    style ID fill:#ccffcc
    style MX fill:#ffcccc
    style PH fill:#ccffcc
```

## 7. CAMADAS DA APLICAÇÃO

```mermaid
graph TB
    subgraph Client["👥 CLIENT LAYER"]
        WEB["🌐 Web Browser<br/>React + TypeScript"]
        MOBILE["📱 Mobile App<br/>React Native"]
    end
    
    subgraph API["🔌 API LAYER"]
        FASTAPI["FastAPI Server<br/>Port 8000"]
        RATELIMIT["Rate Limiter<br/>100 req/min"]
        AUTH["JWT Auth<br/>API Keys"]
    end
    
    subgraph BIZ["🧠 BUSINESS LOGIC"]
        SERVICES["Services<br/>Tendências"]
        PROCESS["Data Processor<br/>Classificação"]
        SCRAPE["Scrapers<br/>Coleta"]
    end
    
    subgraph DATA["💾 DATA LAYER"]
        POSTGRES["PostgreSQL<br/>Dados Principais"]
        REDIS["Redis<br/>Cache"]
        S3["S3 AWS<br/>Arquivos"]
    end
    
    subgraph EXT["🔌 EXTERNAL"]
        TIKTOK["TikTok API<br/>Dados TikTok"]
        PLAYWRIGHT["Playwright<br/>Browser Auto"]
    end
    
    WEB --> FASTAPI
    MOBILE --> FASTAPI
    
    FASTAPI --> RATELIMIT
    RATELIMIT --> AUTH
    AUTH --> SERVICES
    
    SERVICES --> PROCESS
    PROCESS --> POSTGRES
    PROCESS --> REDIS
    PROCESS --> S3
    
    SERVICES --> SCRAPE
    SCRAPE --> TIKTOK
    SCRAPE --> PLAYWRIGHT
    
    POSTGRES -.->|query| SERVICES
    REDIS -.->|cache hit| SERVICES
```

## 8. CONFORMIDADE E SEGURANÇA

```mermaid
graph TB
    subgraph REGIONS["🌍 REGIONS"]
        BR["🇧🇷 LGPD<br/>Brasil"]
        EU["🇪🇺 GDPR<br/>Europa"]
        US["🇺🇸 CCPA<br/>USA"]
        ASIA["🌏 PDPA<br/>Ásia"]
    end
    
    subgraph CONTROLS["🛡️ CONTROLS"]
        CONSENT["Consent<br/>Management"]
        RETENTION["Data<br/>Retention"]
        DELETE["Delete on<br/>Request"]
        PRIVACY["Privacy by<br/>Design"]
    end
    
    subgraph MONITOR["📋 MONITORING"]
        AUDIT["Audit Logs<br/>Todas ações"]
        ENCRYPT["Encryption<br/>at rest"]
        SECURE["Secure<br/>Keys"]
    end
    
    BR --> CONSENT
    EU --> CONSENT
    US --> CONSENT
    ASIA --> CONSENT
    
    BR --> RETENTION
    BR --> DELETE
    EU --> RETENTION
    EU --> DELETE
    US --> RETENTION
    US --> DELETE
    
    CONSENT --> AUDIT
    RETENTION --> ENCRYPT
    DELETE --> SECURE
    
    AUDIT -.->|Compliance Report| Admin
    ENCRYPT -.->|Security Check| CTO
    SECURE -.->|Key Rotation| DevOps
```

## 9. DEPLOYMENT ARCHITECTURE

```mermaid
graph TB
    subgraph Local["💻 LOCAL"]
        CODE["Git Repo<br/>Code"]
        TEST["Pytest<br/>Unit Tests"]
    end
    
    subgraph CI["🔄 CI/CD"]
        GHA["GitHub Actions<br/>Build & Test"]
        ECR["ECR Registry<br/>Docker Image"]
    end
    
    subgraph STAGING["🟡 STAGING"]
        ECS1["ECS Container<br/>Staging"]
        RDS1["RDS Postgres<br/>Staging"]
        REDIS1["ElastiCache<br/>Staging"]
    end
    
    subgraph PROD["🟢 PRODUCTION"]
        K8S["Kubernetes<br/>3 replicas"]
        LB["Load Balancer<br/>Nginx"]
        RDS2["RDS Postgres<br/>Production"]
        REDIS2["ElastiCache<br/>Production"]
    end
    
    subgraph MONITOR["📊 MONITORING"]
        PROM["Prometheus<br/>Métricas"]
        GRAF["Grafana<br/>Dashboards"]
        ALERT["AlertManager<br/>Alertas"]
    end
    
    CODE --> TEST
    TEST --> GHA
    GHA --> ECR
    
    ECR --> STAGING
    STAGING --> PROD
    
    RDS1 -.->|backup diário| RDS2
    REDIS1 -.->|failover| REDIS2
    
    K8S --> PROM
    K8S --> ALERT
    PROM --> GRAF
    ALERT -.->|Slack| OPS
```

## 10. ESTADO DA APLICAÇÃO - MÁQUINA DE ESTADOS

```mermaid
stateDiagram-v2
    [*] --> Idle
    
    Idle --> Collecting: Job triggered
    Idle --> Processing: Manual trigger
    Idle --> Exporting: User export request
    
    Collecting --> Validating: Data received
    Validating --> Cleaning: Format OK
    Cleaning --> Processing: No errors
    Cleaning --> ErrorRecovery: Validation failed
    
    Processing --> Classifying: Data clean
    Classifying --> Enriching: Classification OK
    Enriching --> Storing: Scores computed
    Storing --> Notifying: DB saved
    Notifying --> Idle: Complete
    
    Exporting --> ExportFormatting: Format selected
    ExportFormatting --> Idle: File ready
    
    ErrorRecovery --> Logging: Error logged
    Logging --> Idle: Fallback executed
    
    Idle --> Maintenance: Scheduled
    Maintenance --> DBCleanup: Cleanup
    DBCleanup --> Idle: Done
    
    note right of Collecting
        Tempo: 30-60s
        Status: COLLECTING
    end note
    
    note right of Processing
        Tempo: 10-30s
        Status: PROCESSING
    end note
    
    note right of Storing
        Tempo: 5-10s
        Status: STORING
    end note
```

## 11. MATRIZ DE COMPATIBILIDADE REGIONAL

```mermaid
graph LR
    subgraph Regions
        USA["🇺🇸 USA"]
        BR["🇧🇷 BR"]
        MX["🇲🇽 MX"]
        ID["🇮🇩 ID"]
        EU["🇪🇺 EU"]
    end
    
    subgraph APIAccess["API Oficial"]
        FULL["✅ Completo"]
        RESTRICTED["⚠️ Restrito"]
    end
    
    subgraph Compliance["Conformidade"]
        CCPA["CCPA OK"]
        LGPD["LGPD OK"]
        GDPR["GDPR OK"]
        PDPA["PDPA OK"]
    end
    
    USA --> FULL
    BR --> FULL
    MX --> FULL
    ID --> FULL
    EU --> RESTRICTED
    
    USA --> CCPA
    BR --> LGPD
    MX --> CCPA
    ID --> PDPA
    EU --> GDPR
```

## 12. FLUXO DE DESENVOLVEDOR - WORKFLOW

```mermaid
graph TB
    DEV["👨‍💻 Developer"]
    
    DEV -->|1. Clone| GIT["Git Clone<br/>main branch"]
    GIT -->|2. Setup| SETUP["Setup Local<br/>venv + deps"]
    SETUP -->|3. Config| CONFIG[".env config<br/>API keys"]
    CONFIG -->|4. Test| TEST["pytest<br/>Unit tests"]
    TEST -->|5. Code| CODE["Implementar<br/>Feature"]
    CODE -->|6. Test| TEST2["pytest<br/>Local tests"]
    TEST2 -->|7. Commit| COMMIT["git commit<br/>+ push"]
    COMMIT -->|8. Review| PR["Pull Request<br/>Code Review"]
    PR -->|9. Merge| MERGE["Merge to main<br/>Auto deploy"]
    MERGE -->|10. Verify| VERIFY["Verify Staging<br/>Tests pass"]
    VERIFY -->|Status| OK["✅ Deployed!"]
    
    style DEV fill:#ffcccc
    style OK fill:#ccffcc
    style PR fill:#ffffcc
```

---

**Todos os 12 diagramas Mermaid estão prontos para use em sua documentação!**