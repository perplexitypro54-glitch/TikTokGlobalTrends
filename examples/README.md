# 📚 Examples - TikTok Global Trends

Este diretório contém exemplos práticos de uso do sistema TikTok Global Trends.

## 📋 Exemplos Disponíveis

### 1. example_reporting.py
Demonstra o uso completo do Sistema de Relatório de Ações:
- Criação de logs de auditoria, coleta e conformidade
- Geração de relatórios filtrados
- Exportação em múltiplos formatos (JSON, HTML)

**Como executar:**
```bash
# Certifique-se de que o banco de dados foi inicializado
python scripts/init_database.py

# Execute o exemplo
python examples/example_reporting.py
```

**Saída esperada:**
- Logs de exemplo criados no banco de dados
- Relatórios gerados em JSON e HTML no diretório `reports/`
- Mensagens de sucesso no console

## 🚀 Pré-requisitos

Antes de executar os exemplos:

1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Inicializar banco de dados:**
   ```bash
   python scripts/init_database.py
   ```

3. **Verificar estrutura:**
   ```bash
   python src/main.py
   ```

## 📖 Documentação Relacionada

- **Relatórios**: [docs/RELATORIO_ACOES.md](../docs/RELATORIO_ACOES.md)
- **Guia Rápido**: [QUICK-START.md](../QUICK-START.md)
- **README Principal**: [README.md](../README.md)

## 💡 Dicas

- Os exemplos criam dados de teste no banco de dados
- Execute `scripts/init_database.py` novamente para resetar os dados
- Verifique o diretório `reports/` para ver os relatórios gerados
- Modifique os exemplos para testar diferentes cenários

## 🐛 Problemas Comuns

### Erro: "No module named 'src'"
**Solução:** Execute os exemplos a partir da raiz do projeto:
```bash
cd /path/to/tiktok-global-trends
python examples/example_reporting.py
```

### Erro: "Database not found"
**Solução:** Inicialize o banco de dados primeiro:
```bash
python scripts/init_database.py
```

### Erro: "Permission denied"
**Solução:** Dê permissão de execução:
```bash
chmod +x examples/example_reporting.py
```

## 🔗 Links Úteis

- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/tutorial.html)
- [Python Logging Guide](https://docs.python.org/3/howto/logging.html)
- [LGPD Compliance](https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd)
