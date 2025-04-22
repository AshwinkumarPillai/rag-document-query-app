# Backend - FastAPI + ChromaDB

This is the backend for the project built using FastAPI, powered by ChromaDB for vector storage. It includes Docker support for containerized deployment and environment consistency.

## Tech Stack

- Python 3.11
- FastAPI for the web framework
- Uvicorn as ASGI server
- ChromaDB for vector database
- Docker + Docker Compose for environment setup

## ENV FILE

Rename the .env.example to .env. You will find the `LLM_MODEL_API_KEY=YOUR_KEY` line on top, make sure to add the Groq API KEY

```
LLM_MODEL_API_KEY=YOUR_KEY
```

## SETUP

1. To run with Docker

```bash
docker-compose up --build # start the service
```

```bash
docker-compose down # to stop the service
```

This will:

- Start the ChromaDB service on port 8000
- Start the FastAPI app on port 9000

You can access your FastAPI docs at:
[http://localhost:9000/docs](http://localhost:9000/docs)

2. To run on local machine

- Install the dependencies

```bash
pip install -r requirements.txt
```

- Go to the data/chroma_db folder and start the service

```bash
cd data/chroma_db
chroma run --path .
```

Chroma will run on port 8000

- In the project root start the project (if you are in chroma folder make sure to go back to root of the project)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 9000
```

## Project Structure

```

backend/
├── app/
│ └── main.py # FastAPI app entry point
├── requirements.txt # Python dependencies
├── Dockerfile # Backend Docker image
├── docker-compose.yml # Compose file to run backend + ChromaDB

```

## Volume Storage

ChromaDB stores its data inside:

```bash
./data/chroma_db/
```

This is mounted to persist database storage even after container restarts.
