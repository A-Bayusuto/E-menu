### Setup Instructions:

1. **Fetch Website from Git:** Clone the repository:

    ```bash
    git clone https://github.com/A-Bayusuto/E-menu.git
    ```

2. **Rebuild Database:** Delete the database folders not pushed onto git.

3. **Build Docker Container:** Run the following command:

    ```bash
    docker-compose up --build
    ```

4. **Set Up the Database:** Execute the following commands to set up the database:

    ```bash
    docker-compose run web python manage.py makemigrations
    docker-compose run web python manage.py migrate
    ```

5. **Create Admin:** Create an admin account:

    ```bash
    docker-compose run web python manage.py createsuperuser
    ```

6. **Start the Site:** Start the site:

    ```bash
    docker-compose up
    ```
