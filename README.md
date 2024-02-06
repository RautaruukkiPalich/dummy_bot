Starting the app:
1) install Git, Docker, Docker-compose and all docker requirements

2) clone repo
   ```commandline
   git clone https://github.com/RautaruukkiPalich/dummy_bot
   ```
3) create .env file in . with parameters
    ```bash
    TG_TOKEN= #enter TG token
   
    DB_NAME= #enter database name
    DB_HOST= database
    DB_PORT= #enter database port
    DB_USER= #enter database user
    DB_PASS= #enter database password
   
    PGADMIN_DEFAULT_EMAIL= #enter pgadmin email
    PGADMIN_DEFAULT_PASSWORD= #enter pgadmin password
    PGADMIN_PORT= #enter pgadmin port
    
    REDIS_HOST= redis
    REDIS_PORT= #enter redis port
   ```
4) use command to create and start containers
    ```commandline
    IDE: docker-compose up -d --build
   
    VDS: docker compose up -d --build
    ```
   
5) create database with PGAdmin

6) use command to create migration
    ```commandline
    IDE: docker-compose exec bot alembic upgrade head
   
    VDS: docker compose exec bot alembic upgrade head
    ```

You can stop and start containers with commands:
```commandline
docker-compose start

docker-compose stop
```

be careful with command
```commandline
docker-compose down
```