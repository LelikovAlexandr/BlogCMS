install:
	poetry install

lint:
	poetry run flake8

test:
	coverage run --source='.' manage.py test
	coverage report
	coverage xml

runserver:
	python3 manage.py runserver

runshell:
	python3 manage.py shell

migrate:
	python3 manage.py makemigrations
	python3 manage.py migrate

build:
	poetry build

publish: build
	poetry publish -r $(REPO) -u $(USER) -p $(PASSWORD)