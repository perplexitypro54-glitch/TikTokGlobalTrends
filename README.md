# TikTok Global Trends - Monitoring & Analysis System

A comprehensive system for monitoring and analyzing global TikTok trends across multiple countries using the Official TikTok API, web scraping, and intelligent data processing.

**Status:** 🚀 Phase 1.2 - Models & Integration  
**Python:** ≥3.11  
**Stack:** PySimpleGUI + SQLAlchemy + SQLite

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Development](#development)
- [Project Structure](#project-structure)
- [Documentation](#documentation)

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (check with `python --version`)
- **Git** configured
- **Virtual environment** support (`venv`)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/perplexitypro54-glitch/TikTokGlobalTrends.git
cd TikTokGlobalTrends

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install development dependencies (optional but recommended)
pip install -r requirements-dev.txt

# Install Playwright browsers for web scraping
playwright install chromium
```

### 3. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your TikTok API credentials
# nano .env  # or use your preferred editor
```

### 4. Initialize Database

```bash
# Create database tables and seed initial data
python scripts/init_database.py

# Data will be stored in ./data/tiktok_trends.db (SQLite)
```

### 5. Run Application

```bash
# Start the application
python src/main.py
```

### 6. Keep GitHub Updated

Use these commands whenever you need to push new work or pull the latest changes:

```bash
# Check what changed
git status

# Stage files (repeat as needed)
git add <file-or-folder>  # e.g., git add src/main.py

# Commit with a descriptive message
git commit -m "feat: describe your change"

# Push updates to GitHub (replace main with your current branch)
git push origin main

# Pull the newest changes before starting a new task
git pull --rebase origin main
```

---

## ✨ Features

### Current Phase (MVP)

- ✅ Project structure scaffolding
- ✅ Environment configuration management
- ✅ Logging system with file rotation
- ✅ Database layer with SQLAlchemy (models + ORM integration)
- ✅ Database initialization script with seed data
- ⏳ TikTok Official API client
- ⏳ Web scraper for Creative Center
- ⏳ Data processing pipeline
- ⏳ PySimpleGUI dashboard
- ⏳ Task scheduler and orchestration

### Planned Features

- Multi-country data collection (15+ countries)
- Real-time trend monitoring
- Niche-based content classification
- Compliance with LGPD, GDPR, CCPA, PDPA
- REST API for programmatic access
- Data export (CSV, JSON, Excel)
- Advanced analytics and visualization
- Machine learning trend prediction

---

## 🏗️ Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────┐
│          PySimpleGUI User Interface                  │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│         Orchestrator & Task Scheduler                │
└─────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────┼────────────────┐
        ↓                ↓                 ↓
   ┌─────────┐    ┌─────────┐    ┌──────────────┐
   │ Official│    │ Creative│    │  Playwright  │
   │ API     │    │ Center  │    │  Scraper     │
   │ Client  │    │ Scraper │    │              │
   └─────────┘    └─────────┘    └──────────────┘
        ↓                ↓                 ↓
        └────────────────┼────────────────┘
                         ↓
        ┌────────────────────────────────┐
        │   Data Processing Pipeline     │
        └────────────────────────────────┘
                         ↓
        ┌────────────────────────────────┐
        │   SQLite Database (SQLAlchemy) │
        └────────────────────────────────┘
```

### Key Modules

- **`src/api_clients/`** - Official TikTok API integration
- **`src/scrapers/`** - Web scraping components
- **`src/data_processing/`** - Data cleaning and classification
- **`src/storage/`** - Database layer with SQLAlchemy
- **`src/orchestrator/`** - Task scheduling and coordination
- **`src/utils/`** - Logging, utilities, helpers
- **`src/compliance/`** - GDPR, LGPD, CCPA compliance
- **`src/auth/`** - Authentication and authorization
- **`src/monitoring/`** - Metrics and monitoring
- **`src/ui/`** - PySimpleGUI user interface

---

## 📦 Installation

### System Requirements

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | ≥3.11 | Download from [python.org](https://www.python.org) |
| Git | Latest | For version control |
| OS | macOS, Linux, Windows | All supported |

### Step-by-Step Installation

```bash
# 1. Clone repository
git clone https://github.com/perplexitypro54-glitch/TikTokGlobalTrends.git
cd TikTokGlobalTrends

# 2. Create isolated Python environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS

# 3. Upgrade pip and install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 4. Install Playwright browsers (for web scraping)
playwright install chromium

# 5. (Optional) Install development tools
pip install -r requirements-dev.txt

# 6. Verify installation
python -c "import src; print('✓ Installation successful')"
```

---

## ⚙️ Configuration

### Environment Variables (.env)

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Key variables to configure:

| Variable | Purpose | Example |
|----------|---------|---------|
| `ENVIRONMENT` | Runtime environment | `development` or `production` |
| `TIKTOK_CLIENT_KEY` | TikTok API credentials | Your API key from TikTok Developer |
| `TIKTOK_CLIENT_SECRET` | TikTok API secret | Your API secret |
| `DATABASE_URL` | Database connection | `sqlite:///./data/tiktok_trends.db` |
| `LOG_LEVEL` | Logging verbosity | `INFO`, `DEBUG`, `ERROR` |
| `LOG_DIR` | Log file directory | `./logs` |
| `COMPLIANCE_REGIONS` | Data compliance rules | `LGPD,GDPR,CCPA,PDPA` |

### Database Configuration

The application uses **SQLite** for data storage (ideal for MVP):

```env
# SQLite configuration
DATABASE_URL=sqlite:///./data/tiktok_trends.db
```

For production, consider PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/tiktok_trends
```

---

## ▶️ Running the Application

### Start the Application

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Run the application
python src/main.py
```

### Expected Output

```
INFO - tiktok_global_trends - TikTok Global Trends initialized
```

### Running with Debug Logging

```bash
# Set environment variable for debug logging
export LOG_LEVEL=DEBUG
python src/main.py
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/test_api_client.py -v

# Run with markers
pytest tests/ -v -m unit
```

---

## 👨‍💻 Development

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and test
pytest tests/ -v

# 3. Format code
black src/ tests/
isort src/ tests/

# 4. Run linter
flake8 src/ tests/

# 5. Type checking
mypy src/ --strict

# 6. Commit and push
git add .
git commit -m "feat: Add new feature"
git push origin feature/new-feature
```

### Code Style

- **Formatter:** Black (line length: 100)
- **Import sorter:** isort
- **Linter:** flake8, pylint
- **Type checker:** mypy
- **Security scanner:** bandit

### Running Development Tools

```bash
# Format with Black
black src/ tests/

# Sort imports
isort src/ tests/

# Run all checks
flake8 src/ tests/
mypy src/ --strict
pylint src/

# Security scan
bandit -r src/
```

---

## 📁 Project Structure

```
TikTokGlobalTrends/
│
├── 📄 README.md                   # This file
├── 📄 pyproject.toml              # Project metadata and tool config
├── 📄 requirements.txt            # Runtime dependencies
├── 📄 requirements-dev.txt        # Development dependencies
├── 📄 .env.example                # Example environment variables
├── 📄 .gitignore                  # Git ignore rules
│
├── 📁 src/                        # Main application code
│   ├── __init__.py
│   ├── main.py                    # Entry point
│   │
│   ├── config/
│   │   └── __init__.py
│   │
│   ├── api_clients/               # TikTok API integration
│   │   ├── __init__.py
│   │   └── tiktok_official_client.py
│   │
│   ├── scrapers/                  # Web scraping components
│   │   ├── __init__.py
│   │   └── creative_center_scraper.py
│   │
│   ├── data_processing/           # Data processing pipeline
│   │   ├── __init__.py
│   │   ├── processor.py
│   │   └── niche_classifier.py
│   │
│   ├── storage/                   # Database layer
│   │   ├── __init__.py
│   │   └── database.py
│   │
│   ├── orchestrator/              # Task orchestration
│   │   ├── __init__.py
│   │   └── scheduler.py
│   │
│   ├── utils/                     # Utilities and helpers
│   │   ├── __init__.py
│   │   └── logger.py
│   │
│   ├── compliance/                # Compliance features
│   │   └── __init__.py
│   │
│   ├── auth/                      # Authentication
│   │   └── __init__.py
│   │
│   ├── monitoring/                # Monitoring & metrics
│   │   └── __init__.py
│   │
│   └── ui/                        # PySimpleGUI interface
│       └── __init__.py
│
├── 📁 tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest configuration
│   ├── test_api_client.py
│   └── test_processor.py
│
├── 📁 docs/                       # Documentation
│   └── README.md
│
├── 📁 logs/                       # Application logs
│   ├── app.log
│   ├── errors.log
│   └── audit.log
│
└── 📁 data/                       # Application data (created at runtime)
    └── tiktok_trends.db
```

---

## 📚 Documentation

### Key Documents

- **`QUICK-START.md`** - Quick start guide with timelines
- **`prd-tiktok-trends.md`** - Product requirements document
- **`prompts-por-fases.md`** - Development phase prompts
- **`diagramas-mermaid.md`** - Architecture diagrams
- **`docs/README.md`** - Project documentation

---

## 🔐 Security & Compliance

### Compliance Support

- ✅ LGPD (Brazil)
- ✅ GDPR (Europe)
- ✅ CCPA (California)
- ✅ PDPA (Thailand)

### Security Best Practices

1. **Never commit `.env`** - Use `.env.example` as template
2. **Rotate API keys** - Change credentials regularly
3. **Use HTTPS** - Only secure API endpoints
4. **Encrypt sensitive data** - Use bcrypt for passwords
5. **Run security scans** - Regular `bandit` checks

---

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'src'`

**Solution:**
```bash
# Make sure you're in the project root directory
cd /path/to/TikTokGlobalTrends

# Activate virtual environment
source venv/bin/activate
```

### Issue: `playwright install` fails

**Solution:**
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install -y libgbm1 libxss1

# Then retry
playwright install chromium
```

### Issue: Database lock errors

**Solution:**
```bash
# Remove old database and restart
rm -f data/tiktok_trends.db
python src/main.py
```

---

## 📞 Support & Communication

### Getting Help

- **Issues:** GitHub Issues tracker
- **Discussions:** GitHub Discussions
- **Documentation:** See `docs/` folder

### Reporting Bugs

When reporting issues, include:

```markdown
- Python version: `python --version`
- OS: macOS/Linux/Windows
- Error message: Full traceback
- Steps to reproduce: Sequential steps
- Expected behavior: What should happen
```

---

## 📈 Roadmap

### Phase 1 (Current) - MVP Setup
- [x] Project structure
- [x] Configuration system
- [x] Logging framework
- [ ] Database models

### Phase 2 - Data Collection
- [ ] TikTok API client implementation
- [ ] Web scraper for Creative Center
- [ ] Data validation and error handling
- [ ] Rate limiting and retry logic

### Phase 3 - Processing & Storage
- [ ] Data normalization pipeline
- [ ] Niche classification engine
- [ ] Database persistence
- [ ] Query optimization

### Phase 4 - UI & APIs
- [ ] PySimpleGUI dashboard
- [ ] REST API endpoints
- [ ] Data export features
- [ ] Real-time notifications

### Phase 5 - Compliance & Monitoring
- [ ] GDPR/LGPD/CCPA implementation
- [ ] Audit logging
- [ ] Performance monitoring
- [ ] Security hardening

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👥 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 🎯 Acceptance Criteria Status

- ✅ Fresh checkout allows `pip install -r requirements.txt` without errors on Python ≥3.11
- ✅ `python src/main.py` executes without crashing, logging placeholder message
- ✅ Directory layout matches Fase 1.1 structure
- ✅ Documentation reflects PySimpleGUI + SQLite stack

---

**Last Updated:** November 2025  
**Version:** 0.1.0 (Initial Scaffold)  
**Status:** ✅ Ready for Phase 1 Development
