1. Open a terminal and navigate to the directory containing the Dockerfile. Run the following command to build the Docker image:  
```docker build -t my-python-app .```
2. Use the following command to run the Docker container, mapping port 3000 and mounting the data.json file as a volume:  
```docker run -d -p 3000:3000 -v $(pwd)/storage/data.json:/app/storage/data.json my-python-app```
3. Open a web browser and navigate to http://localhost:3000 to access the application running inside the Docker container.