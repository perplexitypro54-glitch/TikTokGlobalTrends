# 📊 Sistema de Relatório de Ações

## Visão Geral

O **Sistema de Relatório de Ações** do TikTok Global Trends fornece funcionalidades completas de auditoria, logging e geração de relatórios para monitorar todas as ações do sistema, coletas de dados e eventos de conformidade legal.

---

## 🎯 Funcionalidades

### 1. Modelos de Log

#### AuditLog (Log de Auditoria)
Registra todas as ações do sistema e usuários:
- Criação, leitura, atualização e exclusão de recursos
- Chamadas de API
- Login/logout de usuários
- Scraping de dados
- Processamento de dados
- Erros do sistema

**Campos principais:**
- `action_type`: Tipo de ação (CREATE, READ, UPDATE, DELETE, etc.)
- `user_id`: ID do usuário que realizou a ação
- `resource_type`: Tipo de recurso afetado
- `description`: Descrição detalhada da ação
- `status`: Status da operação (SUCCESS, FAILED)
- `execution_time_ms`: Tempo de execução em milissegundos
- `ip_address`: Endereço IP de origem
- `metadata`: Dados adicionais em JSON

#### CollectionLog (Log de Coleta)
Rastreia todas as execuções de coleta de dados:
- Coletas da API Oficial do TikTok
- Scraping do Creative Center
- Scraping com Playwright

**Campos principais:**
- `country_code`: Código do país da coleta
- `data_source`: Fonte dos dados (OFFICIAL_API, CREATIVE_CENTER, PLAYWRIGHT_SCRAPER)
- `status`: Status da coleta (PENDING, RUNNING, SUCCESS, FAILED, etc.)
- `items_collected`: Número de itens coletados
- `items_processed`: Número de itens processados
- `api_calls_made`: Número de chamadas de API realizadas
- `rate_limit_hit`: Se atingiu limite de taxa
- `execution_time_seconds`: Tempo de execução

#### ComplianceLog (Log de Conformidade)
Registra eventos relacionados à conformidade legal:
- Acesso a dados pessoais
- Exportação de dados
- Exclusão de dados
- Consentimento (dado/revogado)
- Violações de segurança
- Solicitações de privacidade

**Campos principais:**
- `regulation`: Regulamentação aplicável (LGPD, GDPR, CCPA, PDPA)
- `event_type`: Tipo de evento de conformidade
- `user_id`: ID do usuário relacionado
- `risk_level`: Nível de risco (LOW, MEDIUM, HIGH)
- `action_required`: Se requer ação
- `action_taken`: Se a ação foi tomada
- `compliance_officer`: Oficial de conformidade responsável

---

## 📈 Tipos de Relatórios

### 1. Relatório de Auditoria
Mostra todas as ações do sistema em um período:

```bash
python scripts/generate_report.py --type audit --days 7 --format json
```

**Filtros disponíveis:**
- `--action-type`: Tipo de ação específica
- `--user-id`: Ações de um usuário específico
- `--status`: Status das ações (SUCCESS, FAILED)
- `--start-date`: Data inicial (YYYY-MM-DD)
- `--end-date`: Data final (YYYY-MM-DD)

### 2. Relatório de Coleta
Mostra todas as coletas de dados realizadas:

```bash
python scripts/generate_report.py --type collection --days 30 --format csv
```

**Filtros disponíveis:**
- `--country`: Código do país (US, BR, MX, etc.)
- `--status`: Status da coleta (SUCCESS, FAILED, RATE_LIMITED)
- `--start-date`: Data inicial
- `--end-date`: Data final

### 3. Relatório de Conformidade
Mostra eventos de conformidade legal:

```bash
python scripts/generate_report.py --type compliance --days 90 --format html
```

**Filtros disponíveis:**
- `--regulation`: Regulamentação (LGPD, GDPR, CCPA, PDPA)
- `--risk-level`: Nível de risco (LOW, MEDIUM, HIGH)
- `--start-date`: Data inicial
- `--end-date`: Data final

### 4. Relatório Resumido
Gera um resumo executivo com estatísticas agregadas:

```bash
python scripts/generate_report.py --type summary --days 30 --format html
```

**Inclui:**
- Total de ações por tipo
- Taxa de sucesso/falha
- Total de itens coletados
- Incidentes de rate limit
- Eventos de conformidade por regulamentação
- Eventos de alto risco pendentes

---

## 🎨 Formatos de Saída

### JSON
Formato estruturado ideal para processamento programático:
```bash
--format json
```

### CSV
Formato tabular para análise em Excel/Planilhas:
```bash
--format csv
```

### HTML
Relatório visual formatado para visualização em navegador:
```bash
--format html
```

### TEXT
Formato de texto simples:
```bash
--format text
```

---

## 💻 Exemplos de Uso

### Exemplo 1: Auditoria de Ações de um Usuário Específico
```bash
python scripts/generate_report.py \
  --type audit \
  --user-id 1 \
  --days 30 \
  --format html \
  --output reports/user_1_audit.html
```

### Exemplo 2: Coletas com Falha nos Últimos 7 Dias
```bash
python scripts/generate_report.py \
  --type collection \
  --status FAILED \
  --days 7 \
  --format csv \
  --output reports/failed_collections.csv
```

### Exemplo 3: Eventos LGPD de Alto Risco
```bash
python scripts/generate_report.py \
  --type compliance \
  --regulation LGPD \
  --risk-level HIGH \
  --days 90 \
  --format json
```

### Exemplo 4: Relatório Executivo Mensal
```bash
python scripts/generate_report.py \
  --type summary \
  --start-date 2025-01-01 \
  --end-date 2025-01-31 \
  --format html \
  --output reports/monthly_summary_jan_2025.html
```

---

## 🔧 Uso Programático

### Criar Log de Auditoria

```python
from src.storage.models import AuditLog, ActionType
from src.storage.database import DatabaseManager

db = DatabaseManager("sqlite:///./data/tiktok_trends.db")

with db.get_session() as session:
    audit_log = AuditLog(
        action_type=ActionType.CREATE,
        user_id=1,
        username="admin",
        resource_type="Video",
        resource_id="12345",
        description="Created new video record",
        status="SUCCESS",
        execution_time_ms=120
    )
    session.add(audit_log)
    session.commit()
```

### Criar Log de Coleta

```python
from datetime import datetime
from src.storage.models import CollectionLog, CollectionStatus
from src.storage.models.enums import CountryCode, DataSourceType

with db.get_session() as session:
    collection_log = CollectionLog(
        country_code=CountryCode.BR,
        data_source=DataSourceType.OFFICIAL_API,
        status=CollectionStatus.SUCCESS,
        started_at=datetime.now(),
        completed_at=datetime.now(),
        items_collected=150,
        items_processed=150,
        api_calls_made=5,
        execution_time_seconds=12.5
    )
    session.add(collection_log)
    session.commit()
```

### Criar Log de Conformidade

```python
from src.storage.models import ComplianceLog, ComplianceRegulation, ComplianceEventType

with db.get_session() as session:
    compliance_log = ComplianceLog(
        regulation=ComplianceRegulation.LGPD,
        event_type=ComplianceEventType.DATA_ACCESS,
        user_id=10,
        user_email="user@example.com",
        description="User accessed personal data report",
        risk_level="LOW",
        action_required=False
    )
    session.add(compliance_log)
    session.commit()
```

### Gerar Relatório Programaticamente

```python
from src.reporting import ReportGenerator, ReportFormat
from datetime import datetime, timedelta
from pathlib import Path

with db.get_session() as session:
    generator = ReportGenerator(session)
    
    # Gerar relatório de auditoria
    start_date = datetime.now() - timedelta(days=7)
    report_data = generator.generate_audit_report(start_date=start_date)
    
    # Exportar para JSON
    output_path = Path("reports/audit_last_7_days.json")
    generator.export_report(report_data, ReportFormat.JSON, output_path)
```

---

## 📊 Estrutura das Tabelas

### audit_logs
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER | ID único |
| action_type | VARCHAR(50) | Tipo de ação |
| user_id | INTEGER | ID do usuário |
| username | VARCHAR(100) | Nome do usuário |
| resource_type | VARCHAR(100) | Tipo de recurso |
| resource_id | VARCHAR(255) | ID do recurso |
| description | TEXT | Descrição da ação |
| status | VARCHAR(20) | Status (SUCCESS/FAILED) |
| ip_address | VARCHAR(45) | IP de origem |
| execution_time_ms | INTEGER | Tempo de execução (ms) |
| error_message | TEXT | Mensagem de erro |
| metadata | TEXT | Dados adicionais (JSON) |
| created_at | TIMESTAMP | Data/hora de criação |
| updated_at | TIMESTAMP | Data/hora de atualização |

### collection_logs
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER | ID único |
| country_code | VARCHAR(2) | Código do país |
| data_source | VARCHAR(50) | Fonte dos dados |
| status | VARCHAR(50) | Status da coleta |
| started_at | TIMESTAMP | Início da coleta |
| completed_at | TIMESTAMP | Término da coleta |
| execution_time_seconds | FLOAT | Tempo de execução |
| items_collected | INTEGER | Itens coletados |
| items_processed | INTEGER | Itens processados |
| items_failed | INTEGER | Itens com falha |
| api_calls_made | INTEGER | Chamadas de API |
| rate_limit_hit | BOOLEAN | Se atingiu rate limit |
| error_message | TEXT | Mensagem de erro |
| retry_count | INTEGER | Tentativas de retry |
| metadata | TEXT | Dados adicionais (JSON) |
| created_at | TIMESTAMP | Data/hora de criação |
| updated_at | TIMESTAMP | Data/hora de atualização |

### compliance_logs
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER | ID único |
| regulation | VARCHAR(20) | Regulamentação |
| event_type | VARCHAR(50) | Tipo de evento |
| user_id | INTEGER | ID do usuário |
| user_email | VARCHAR(255) | Email do usuário |
| description | TEXT | Descrição do evento |
| resource_type | VARCHAR(100) | Tipo de recurso |
| resource_id | VARCHAR(255) | ID do recurso |
| action_required | BOOLEAN | Requer ação |
| action_taken | BOOLEAN | Ação tomada |
| action_details | TEXT | Detalhes da ação |
| compliance_officer | VARCHAR(100) | Oficial responsável |
| reviewed_at | TIMESTAMP | Data de revisão |
| risk_level | VARCHAR(20) | Nível de risco |
| ip_address | VARCHAR(45) | IP de origem |
| metadata | TEXT | Dados adicionais (JSON) |
| created_at | TIMESTAMP | Data/hora de criação |
| updated_at | TIMESTAMP | Data/hora de atualização |

---

## 🔍 Índices de Performance

Índices criados para otimizar consultas:

### audit_logs
- `idx_audit_action_type` (action_type)
- `idx_audit_user_id` (user_id)
- `idx_audit_resource` (resource_type, resource_id)
- `idx_audit_created_at` (created_at)
- `idx_audit_status` (status)

### collection_logs
- `idx_collection_country` (country_code)
- `idx_collection_source` (data_source)
- `idx_collection_status` (status)
- `idx_collection_started` (started_at)
- `idx_collection_completed` (completed_at)

### compliance_logs
- `idx_compliance_regulation` (regulation)
- `idx_compliance_event_type` (event_type)
- `idx_compliance_user_id` (user_id)
- `idx_compliance_created_at` (created_at)
- `idx_compliance_risk_level` (risk_level)
- `idx_compliance_action_required` (action_required)

---

## ⚡ Performance

### Recomendações:
1. **Período de retenção**: Configurar limpeza automática de logs antigos (ex: 90-365 dias)
2. **Particionamento**: Para volumes grandes, considerar particionamento por data
3. **Arquivamento**: Mover logs antigos para storage frio (S3, etc.)
4. **Agregação**: Criar tabelas de agregação para relatórios frequentes

---

## 🔐 Segurança e Conformidade

### Dados Sensíveis
- IPs são armazenados para auditoria (conformidade LGPD/GDPR)
- Emails são pseudonimizados quando possível
- Metadados são criptografados em produção

### Retenção de Dados
| Tipo de Log | Período de Retenção | Regulamentação |
|-------------|---------------------|----------------|
| Audit Logs | 365 dias | LGPD/GDPR |
| Collection Logs | 180 dias | Operacional |
| Compliance Logs | 2555 dias (7 anos) | LGPD Art. 16 |

### Direitos dos Usuários
- **Direito de acesso**: Relatórios filtrados por user_id
- **Direito ao esquecimento**: Anonimização de dados de usuário
- **Portabilidade**: Exportação em JSON/CSV

---

## 📝 Manutenção

### Limpeza de Logs Antigos
```python
from datetime import datetime, timedelta
from src.storage.database import DatabaseManager
from src.storage.models import AuditLog

db = DatabaseManager("sqlite:///./data/tiktok_trends.db")

with db.get_session() as session:
    # Deletar logs de auditoria com mais de 365 dias
    cutoff_date = datetime.now() - timedelta(days=365)
    session.query(AuditLog).filter(
        AuditLog.created_at < cutoff_date
    ).delete()
    session.commit()
```

### Backup de Logs
```bash
# Exportar todos os logs para backup
python scripts/generate_report.py --type audit --days 365 --format json --output backups/audit_backup.json
python scripts/generate_report.py --type collection --days 365 --format json --output backups/collection_backup.json
python scripts/generate_report.py --type compliance --days 365 --format json --output backups/compliance_backup.json
```

---

## 🐛 Troubleshooting

### Problema: Relatório vazio
**Solução**: Verificar se há logs no período especificado
```bash
python scripts/generate_report.py --type audit --days 90
```

### Problema: Erro ao exportar CSV
**Solução**: CSV requer dados em lista. Use JSON para relatórios summary:
```bash
python scripts/generate_report.py --type summary --format json
```

### Problema: Performance lenta
**Solução**: 
1. Reduzir período do relatório
2. Adicionar filtros específicos
3. Executar limpeza de logs antigos

---

## 📚 Referências

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [LGPD - Lei Geral de Proteção de Dados](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [GDPR - General Data Protection Regulation](https://gdpr.eu/)
- [CCPA - California Consumer Privacy Act](https://oag.ca.gov/privacy/ccpa)
- [PDPA - Personal Data Protection Act](https://www.pdpc.gov.sg/Overview-of-PDPA/The-Legislation/Personal-Data-Protection-Act)

---

**Última atualização**: 2025-11-13  
**Versão**: 1.0.0  
**Autor**: TikTok Global Trends Team
