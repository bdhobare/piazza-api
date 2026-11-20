# Piazza API
This repository contains the API for Piazza application. Piazza allows users to publish posts by topic,
react and comment. Expired posts accept no further interactions. The API is developed with FastAPI, sqlite, Docker and Kubernetes.

## Prerequisites
1. Python 3.10+, pip
2. [Docker](https://www.docker.com/get-started/) installed locally.
3. (optional) Account created on [Docker Hub](https://app.docker.com/accounts/bdhobare).

## Running Locally
Run the following commands from the project root:

1. Create and activate a virtual environment.

On macOS/Linux:
```
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:
```
python -m venv .venv
.venv\Scripts\Activate.ps1
```
2. Install the requirements.
```
python -m pip install -r requirements.txt
```
3. Make a working configuration file.
```
cp -i .env.example .env
```
4. Generate a secret
```
python -c "import secrets; print(secrets.token_hex(32))"
```
5. On macOS/Linux:
```
export JWT_SECRET="paste-your-generated-value-here"
```
On Windows PowerShell:
```
$env:JWT_SECRET = "paste-your-generated-value-here"
```
Keep the value private and reuse it after restarting the terminal.
6. Run the app:
```
uvicorn main:app --reload
```
7. Open FastAPI docs:

http://127.0.0.1:8000/docs

8. Type Ctrl+C to stop the server.

## Running tests
```
python -m pytest
```

## Building and running the docker image locally
1. Build and tag the docker image.
```
export DOCKER_USER_NAME=<YOUR_DOCKER_USERNAME>

docker build --tag $DOCKER_USER_NAME/piazza-api:latest .
```
2. Run the image as a container.
```
docker volume create piazza-api-data
docker run -d --name piazza-api -p 80:8000 \
    --env-file .env \
    --mount type=volume,source=piazza-api-data,target=/data \
    $DOCKER_USER_NAME/piazza-api:latest
```
3. Open FastAPI docs.

http://127.0.0.1/docs

4. Clean up the container and volume

```
docker stop piazza-api
docker rm --force piazza-api
docker volume rm piazza-api-data
```
5. Publish image to Docker Hub.
```
docker login
docker push $DOCKER_USER_NAME/piazza-api
```

## Running it in kubernetes
TODO