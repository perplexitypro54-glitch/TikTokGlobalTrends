# TikTok Global Trends - Documentation

This directory contains comprehensive documentation for the TikTok Global Trends project.

## 📚 Documentation Files

### Overview
- **`..` /README.md** - Main project README with setup and usage instructions

### Architecture & Design
- **`../diagramas-mermaid.md`** - Architecture diagrams in Mermaid format
- **`../prd-tiktok-trends.md`** - Product Requirements Document (PRD)

### Development
- **`../prompts-por-fases.md`** - Structured prompts for each development phase
- **`../QUICK-START.md`** - Quick start guide with timelines and workflows

### Configuration
- **`../.env.example`** - Example environment variables template

## 🚀 Getting Started

### First Time Setup

1. **Read the README** - Main project documentation
   ```bash
   cat ../README.md
   ```

2. **Review the Quick Start** - Get up and running
   ```bash
   cat ../QUICK-START.md
   ```

3. **Understand the Architecture** - Review the design
   ```bash
   cat ../diagramas-mermaid.md
   ```

### Development Phases

Each phase has structured prompts in `../prompts-por-fases.md`:

- **FASE 1**: Setup & Database (Current)
- **FASE 2**: Data Collection
- **FASE 3**: Data Processing
- **FASE 4**: Orchestration
- **FASE 5**: Storage & API
- **FASE 6**: UI & Dashboard
- **FASE 7**: Compliance
- **FASE 8-10**: Monitoring & Production

## 📋 Key Concepts

### Project Stack
- **UI**: PySimpleGUI
- **Backend**: FastAPI (future)
- **Database**: SQLAlchemy + SQLite (MVP), PostgreSQL (production)
- **Web Scraping**: Playwright + BeautifulSoup4
- **Task Scheduling**: APScheduler
- **Data Processing**: Pandas + NumPy

### Directory Structure
```
src/
├── api_clients/         # TikTok API integration
├── scrapers/            # Web scraping components
├── data_processing/     # Data cleaning and classification
├── storage/             # Database layer
├── orchestrator/        # Task orchestration
├── utils/               # Utilities and logging
├── compliance/          # GDPR/LGPD/CCPA
├── auth/                # Authentication
├── monitoring/          # Metrics and monitoring
└── ui/                  # PySimpleGUI interface
```

## 🔧 Common Tasks

### Installation
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the Application
```bash
python src/main.py
```

### Running Tests
```bash
pytest tests/ -v --cov=src
```

### Code Quality
```bash
# Format
black src/ tests/
isort src/ tests/

# Lint
flake8 src/ tests/
mypy src/ --strict

# Security
bandit -r src/
```

## 📞 Support

- **Issues**: GitHub Issues tracker
- **Documentation**: This directory
- **Quick Help**: `../QUICK-START.md`

## 🔍 Additional Resources

- [SQLAlchemy Docs](https://docs.sqlalchemy.org)
- [Playwright Docs](https://playwright.dev/python/)
- [PySimpleGUI Docs](https://pysimplegui.readthedocs.io)
- [APScheduler Docs](https://apscheduler.readthedocs.io)

---

**Last Updated**: November 2025
**Version**: 0.1.0
