# Unkot - Polish Law Monitoring Research

> **Personal Project**: Exploring automated legal change detection for Polish legislation. A long-term personal learning initiative in web application development and legal text processing.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## About This Project

This is a personal exploration of automated legal monitoring systems, developed over several years during my free time. The project investigates practical approaches to tracking Polish legislative changes and notification systems.

**Learning Focus**: Full-stack web development, legal document processing, automated monitoring systems, and Django best practices.

## Technical Exploration

The project serves as a learning platform for:

- **Django Development**: Advanced patterns, Celery integration, i18n support
- **Legal Document Processing**: Parsing and tracking legislative changes
- **Notification Systems**: Email alerts and subscription management
- **Production Patterns**: Docker deployment, monitoring, testing strategies

## Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis (for Celery)
- Docker (optional)

### Local Development

1. **Set up Python environment**:
   ```bash
   pyenv install 3.11.7
   pyenv shell 3.11.7
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements/local.txt
   ```

3. **Configure environment**:
   ```bash
   source env-local.sh
   ```

4. **Run development server**:
   ```bash
   python manage.py runserver
   ```

### Celery Background Tasks

Run Celery worker for background processing:
```bash
celery -A config.celery_app worker --beat --loglevel=info
```

### Internationalization

```bash
# Update translations
./manage.py makemessages --all --ignore 'venv/*'

# Compile translations
./manage.py compilemessages --ignore 'venv/*'
```

## Testing

```bash
# Run tests with coverage
coverage run -m pytest
coverage html
open htmlcov/index.html

# Type checking
mypy unkot
```

## Key Features Explored

- **Legal Document Parsing**: Automated extraction from Polish legal databases
- **Change Detection**: Identifying modifications in legal texts
- **User Subscriptions**: Personalized monitoring preferences
- **Email Notifications**: Automated alerts for relevant changes
- **Multi-language Support**: Polish and English interfaces

## Technology Stack

- **Framework**: Django 4.x with Cookiecutter template
- **Task Queue**: Celery with Redis backend
- **Database**: PostgreSQL
- **Development**: Docker, pytest, mypy
- **Code Quality**: Black formatter, type hints

## Personal Learning Outcomes

Through this project, I've explored:

- Full-stack Django application architecture
- Asynchronous task processing at scale
- Legal document parsing challenges
- Production deployment patterns
- User subscription and notification systems

## Future Explorations

Areas for continued personal research:

- Machine learning for legal change prediction
- Natural language processing for legal texts
- Real-time streaming of legal updates
- Advanced search and filtering capabilities

## Docker Development

For containerized development:
```bash
# See cookiecutter-django documentation for Docker setup
docker-compose up
```

MailHog available at: `http://127.0.0.1:8025` for email testing

## License

This personal research project is private. Shared for demonstration purposes only.

---

*This is a personal project developed during my free time for learning and skill development. It represents my exploration of web application development and legal document processing challenges.*

## Note

This project was initiated as a learning exercise and portfolio demonstration. While functional, it serves primarily as a technical exploration rather than a production service.
