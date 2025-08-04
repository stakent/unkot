# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Unkot is a Polish Legal Monitoring System that provides automated notifications for legal document changes.

## Development Environment Setup
- Python Version: 3.11.7
- Virtual Environment: Use `python -m venv venv && . venv/bin/activate`
- Dependencies: `pip install -r requirements/local.txt`
- Pre-commit: `pre-commit install`

## Common Commands
- Install dependencies: `make deps`
- Run server: `make run` (on port 8001)
- Run debug server: `make run-debug`
- Run tests: `make test`
- Clean environment: `make distclean`

## Internationalization
- Create message files: `make i18n-makemessages`
- Compile message files: `make i18n-compilemessages`

## Architecture Highlights
- Django-based web application
- Celery for async document processing
- PostgreSQL for full-text search
- Containerized deployment
- Event-driven notification system

## Linting and Code Quality
- Uses pre-commit hooks
- Ruff for formatting and linting (per global instructions)
- Black for code formatting

## Testing
- Django test runner used
- Run tests with `make test`
- Test configuration in `pytest.ini`
