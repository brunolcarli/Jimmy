install:
	pip install -r requirements.txt

shell:
	python manage.py shell

run:
	python manage.py runserver 0.0.0.0:6161
