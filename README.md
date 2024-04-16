# E-menu

Fetch webstite from git
Step 1:
Clone git clone https://github.com/A-Bayusuto/E-menu.git

To rebuild from scratch database folders not pushed onto git
Step 2:
Delete data db folder

Build docker container
Step 3:
Run command: docker-compose up --build

Sets the database
Step 4:
docker-compose run web python manage.py makemigrations
docker-compose run web python manage.py migrate

Create admin
Step 5:
docker-compose run web python manage.py createsuperuser

start site
Step 6:
docker-compose up