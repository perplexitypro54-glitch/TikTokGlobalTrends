# 🚀 Início Rápido - Sistema de Relatório de Ações

## O que foi implementado?

Um sistema completo de **auditoria, logging e geração de relatórios** para o TikTok Global Trends.

---

## ⚡ Uso em 3 Passos

### 1️⃣ Inicializar o Banco de Dados
```bash
python scripts/init_database.py
```

### 2️⃣ Executar o Exemplo
```bash
python examples/example_reporting.py
```
Isso irá:
- Criar logs de exemplo (audit, collection, compliance)
- Gerar relatórios em JSON e HTML
- Salvar em `reports/`

### 3️⃣ Gerar Seus Próprios Relatórios
```bash
# Relatório de auditoria dos últimos 7 dias
python scripts/generate_report.py --type audit --days 7 --format json

# Relatório de coletas em HTML
python scripts/generate_report.py --type collection --days 30 --format html

# Resumo executivo
python scripts/generate_report.py --type summary --format html
```

---

## 📊 Tipos de Relatórios

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| **audit** | Todas as ações do sistema | `--type audit --days 30` |
| **collection** | Coletas de dados do TikTok | `--type collection --country BR` |
| **compliance** | Eventos de conformidade legal | `--type compliance --regulation LGPD` |
| **summary** | Resumo executivo com estatísticas | `--type summary --format html` |

---

## 🎨 Formatos de Exportação

- **JSON** - Dados estruturados (ideal para APIs)
- **CSV** - Planilhas (Excel/Google Sheets)
- **HTML** - Relatórios visuais (abrir no navegador)
- **TEXT** - Texto simples

---

## 💻 Uso Programático

```python
from src.reporting import ReportGenerator
from src.storage.database import DatabaseManager

# Conectar ao banco
db = DatabaseManager("sqlite:///./data/tiktok_trends.db")

# Gerar relatório
with db.get_session() as session:
    generator = ReportGenerator(session)
    
    # Relatório dos últimos 7 dias
    from datetime import datetime, timedelta
    start = datetime.now() - timedelta(days=7)
    report = generator.generate_audit_report(start_date=start)
    
    print(f"Total de ações: {len(report)}")
```

---

## 🔍 Exemplos de Filtros

```bash
# Ações de um usuário específico
python scripts/generate_report.py --type audit --user-id 1

# Coletas com falha
python scripts/generate_report.py --type collection --status FAILED

# Eventos LGPD de alto risco
python scripts/generate_report.py --type compliance --regulation LGPD --risk-level HIGH

# Período específico
python scripts/generate_report.py --type audit --start-date 2025-01-01 --end-date 2025-01-31
```

---

## 📚 Documentação Completa

- **Guia Completo:** [docs/RELATORIO_ACOES.md](docs/RELATORIO_ACOES.md)
- **Relatório de Implementação:** [RELATORIO_IMPLEMENTACAO_ACOES.md](RELATORIO_IMPLEMENTACAO_ACOES.md)
- **Exemplos:** [examples/README.md](examples/README.md)

---

## 🆘 Precisa de Ajuda?

```bash
# Ver todas as opções disponíveis
python scripts/generate_report.py --help

# Executar exemplo completo
python examples/example_reporting.py

# Ver documentação
cat docs/RELATORIO_ACOES.md
```

---

## ✅ Checklist

- [ ] Banco de dados inicializado? (`python scripts/init_database.py`)
- [ ] Exemplo executado? (`python examples/example_reporting.py`)
- [ ] Relatórios gerados? (verifique o diretório `reports/`)
- [ ] Documentação lida? (`docs/RELATORIO_ACOES.md`)

---

**Pronto para usar!** 🎉

Para mais detalhes, veja a [documentação completa](docs/RELATORIO_ACOES.md).
