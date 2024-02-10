.ONESHELL:

PYTHON_VERSION := 3.11.7

# Activate venv
ACTIVATE_VENV := . venv/bin/activate && \
				 . ./env-local.sh

# Python Installation Commands
INSTALL_PY_ENV_COMMAND := pyenv install $(PYTHON_VERSION) --skip-existing
ACTIVATE_PY_ENV_COMMAND := pyenv local $(PYTHON_VERSION)

# Install pyenv
install-python:
	@echo Install Python Version: $(PYTHON_VERSION)
	$(INSTALL_PY_ENV_COMMAND)
	@echo Activate Python Version: $(PYTHON_VERSION)
	$(ACTIVATE_PY_ENV_COMMAND)

venv:
	python -m venv venv && \
	$(ACTIVATE_VENV)

deps:
	$(ACTIVATE_VENV) && \
	pip install -r requirements/local.txt && \
	pip install --upgrade pip && \
	pre-commit install

i18n-makemessages:
	./manage.py makemessages --all --ignore 'venv/*'

i18n-compilemessages:
	./manage.py compilemessages --ignore 'venv/*'

test:
	$(ACTIVATE_VENV) && \
	./manage.py test --no-input --keepdb

run:
	$(ACTIVATE_VENV) && \
	./manage.py runserver 8001

run-debug:
	$(ACTIVATE_VENV) && \
	DJANGO_DEBUG=true ./manage.py runserver 8001

distclean:
	rm -rf venv && \
	find -name '__pycache__' | xargs rm -rf
