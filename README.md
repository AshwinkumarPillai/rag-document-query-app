# Full Stack AI-Powered App — React + FastAPI + ChromaDB

This is a full-stack project built using React for the frontend and FastAPI + ChromaDB for the backend. The backend leverages vector storage and machine learning integrations (e.g., HuggingFace), while the frontend offers an interactive user interface built with Create React App.

## Tech Stack

### Frontend

- React (Create React App)
- TypeScript

### Backend

- Python 3.11
- FastAPI (web API)
- Uvicorn (ASGI server)
- ChromaDB (vector database)
- Docker + Docker Compose (for containerization)

## Prerequisites

- Node.js
- Python 3.11
- Docker & Docker Compose (for container-based workflow)

## Backend Setup

### ENV FILE

Rename the .env.example to .env. You will find the `LLM_MODEL_API_KEY=YOUR_KEY` line on top, make sure to add the Groq API KEY

```
LLM_MODEL_API_KEY=YOUR_KEY
```

```bash
cd backend
```

### Option 1: Run with Docker (Recommended)

```bash
docker-compose up --build
```

This will:

- Start the ChromaDB service on port 8000
- Start the FastAPI backend on port 9000

You can access your FastAPI docs at:
[http://localhost:9000/docs](http://localhost:9000/docs)

### Option 2: Run Locally (Frontend + Backend + ChromaDB)

1. Install the dependencies

```bash
pip install -r requirements.txt
```

2. Go to the data/chroma_db folder and start the service

```bash
cd data/chroma_db
chroma run --path .
```

- Chroma will run on port 8000

3. In the project root start the project (if you are in chroma folder make sure to go back to root of the project)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 9000
```

## Frontend Setup

1. Navigate to the frontend folder:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the frontend:

```bash
npm start
```

- Frontend will be running on → http://localhost:3000

## Folder Structure

```
.
├── README.md
├── backend
│   ├── Dockerfile
│   ├── README.md
│   ├── app
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-311.pyc
│   │   │   ├── config.cpython-311.pyc
│   │   │   ├── main.cpython-311.pyc
│   │   │   ├── rag_pipeline.cpython-311.pyc
│   │   │   └── utils.cpython-311.pyc
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── rag_pipeline.py
│   │   └── utils.py
│   ├── data
│   │   ├── chroma_db
│   │   ├── chroma_db_local
│   │   └── uploads
│   ├── docker-compose.yaml
│   └── requirements.txt
└── frontend
    ├── README.md
    ├── package-lock.json
    ├── package.json
    ├── public
    │   ├── favicon.ico
    │   ├── index.html
    │   ├── logo192.png
    │   ├── logo512.png
    │   ├── manifest.json
    │   └── robots.txt
    ├── src
    │   ├── App.css
    │   ├── App.test.tsx
    │   ├── App.tsx
    │   ├── api
    │   │   └── api.ts
    │   ├── components
    │   │   ├── ChatControls
    │   │   │   ├── ChatControls.css
    │   │   │   └── ChatControls.tsx
    │   │   ├── ChatWindow
    │   │   │   ├── ChatWindow.css
    │   │   │   └── ChatWindow.tsx
    │   │   ├── FileUpload
    │   │   │   └── FileUpload.tsx
    │   │   └── MessageInput
    │   │       ├── MessageInput.css
    │   │       └── MessageInput.tsx
    │   ├── index.css
    │   ├── index.tsx
    │   ├── logo.svg
    │   ├── react-app-env.d.ts
    │   ├── reportWebVitals.ts
    │   ├── setupTests.ts
    │   └── types
    │       └── index.ts
    └── tsconfig.json

```
