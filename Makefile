install:
	pip install -r requirements.txt

shell:
	python manage.py shell

migrate:
	python manage.py makemigrations
	python manage.py migrate

run:
	python manage.py runserver 0.0.0.0:6161

pipe_run:
	make install
	make migrate
	make run
