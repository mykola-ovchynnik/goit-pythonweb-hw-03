# My Python App

## Running the Application with Docker Compose

1. Open a terminal and navigate to the root directory.
2. Use the following command to start the application with Docker Compose:
    ```sh
    docker-compose up -d
    ```

## Accessing the Application

1. Open a web browser and navigate to [http://localhost:3000](http://localhost:3000) to access the application running
   inside the Docker container.

## Stopping the Docker Container

1. Use the following command to stop the Docker container without deleting it:
    ```sh
    docker-compose stop
    ```

2. Use the following command to stop and delete the Docker container:
    ```sh
    docker-compose down
    ```

## Checking the Docker Container

1. Use the following command to list all running Docker containers:
    ```sh
    docker ps
    ```
2. Use the following command to view the logs of the running container:
    ```sh
    docker-compose logs
    ```