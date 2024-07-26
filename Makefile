#include .env
#export $(shell sed 's/=.*//' .env)

MANAGE = python manage.py
SOURCE = src
MAIN = core

PROJECT_DIR=$(shell pwd)
WSGI_PORT=8000

# ##########################################################################
# common commands

run:
	$(MANAGE) runserver 127.0.0.1:8000

gunicorn-run:
	gunicorn core.wsgi:application -b 0.0.0.0:8000 --reload

migrations:
	$(MANAGE) makemigrations --no-input
	$(MANAGE) migrate --no-input
	$(MANAGE) flush --no-input
	python seed/seed_script.py
	$(MANAGE) collectstatic --no-input
	gunicorn core.wsgi:application -b 0.0.0.0:8000 --reload


gen-users:
	$(MANAGE) gen_users

gen-s:
	$(MANAGE) gen_seances

kill-port:
	sudo fuser -k 8000/tcp

diagram:
	$(MANAGE) graph_models -a -g -o my_project_visualized.png

start-app:
	cd $(SOURCE) && python manage.py startapp $(app)

migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

shell: # only after 'make extensions-install'
	$(MANAGE) shell_plus --print-sql

freeze:
	pip freeze > requirements.txt

# ##########################################################################
# Celery

worker:
	cd $(PROJECT_DIR) && celery -A $(MAIN) worker --autoscale=4,2 -l info

beat:
	cd $(SOURCE)/&& celery -A $(MAIN) beat -l info

worker-info:
	cd $(SOURCE) && celery -A $(MAIN) events

# ##########################################################################
# Uncommon commands

super:
	$(MANAGE) createsuperuser

install:
	pip install -r requirements.txt

check:
	$(MANAGE) check

migrations-dry:
	$(MANAGE) makemigrations --dry-run

gen-book-category:
	$(MANAGE) gen_book_category


# ##########################################################################
# Installations

flake8-install:
	pip install flake8
	pip install flake8-import-order # сортировку импортов
	pip install flake8-docstrings # доки есть и правильно оформлены
	pip install flake8-builtins # что в коде проекта нет переменных с именем из списка встроенных имён
	pip install flake8-quotes # проверять кавычки

	# ставим гит-хук
	flake8 --install-hook git
	git config --bool flake8.strict true

debugger-install:
	pip install django-debug-toolbar
	# 'debug_toolbar'                                    | add to the INSTALLED_APPS in settings.py
	# debug_toolbar.middleware.DebugToolbarMiddleware    | add to the MIDDLEWARE in settings.py
	# INTERNAL_IPS = [ "127.0.0.1", ]					 | create in the settings.py
	# path('__debug__/', include(debug_toolbar.urls))    | add to the urls.py in project DIR
	# import debug_toolbar                               | add to the urls.py in project DIR

extensions-install:
	pip install django-extensions
	pip install ipython
	# 'django_extensions'                                | add to the INSTALLED_APPS in settings.py

celery-install:
	pip install -U Celery
	pip install flower
#	ubuntu: sudo apt-get install -y erlang
#			sudo apt-get install rabbitmq-server
#			systemctl enable rabbitmq-server
#			systemctl start rabbitmq-server
#			systemctl status rabbitmq-server
#
#	settings.py:
#			CELERY_BROKEN_URL = 'amqp://localhost'
#	celery.py:
#			import os
#			from celery import Celery
#
#			os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
#
#			app = Celery('mysite')
#			app.config_from_object('django.conf:settings', namespace='CELERY')
#			app.autodiscover_tasks()
#	__init__.py:
#  			from .celery import app as celery_app
#
#			__all__ = ['celery_app']



# worker-info-web:
#	in basic console:
#   pip install flower
#   source venv/bin/activate
#	cd *my_proj*
#	celery -A *my_proj* flower

#	ps aux | grep celery
#   pkill -f csp_build.py   its a grep based kill

# signals
#        error_messages = {
#            NON_FIELD_ERRORS: {
#                'unique_together': "%(model_name)s's %(field_labels)s are not unique.",
#            },
#            'email_to': {
#                'required': "Email field is empty.",
#                'invalid': "Enter a valid email address.",
#            },
#        }