# An example of clinical decision-making dashboard

A web application for tracking symptoms and physiological data. 

## Prerequisites

- Node.js (v16 or higher)
- Python 3.8+
- MongoDB
- OpenAI API key

## Environment Setup

### Backend Configuration

Create a `.env` file in the `backend` directory:

```env
MONGO_URI=mongodb:xxx
OPENAI_API_KEY=your_openai_key_here
```

### Frontend Configuration

Create a `.env` file in the `frontend` directory:

```env
VITE_API_BASE_URL=xxx
```

## Installation

### Backend Setup

```bash
cd backend
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Unix/macOS
.\venv\Scripts\activate   # Windows

pip install -r requirements.txt

python -m app.run
```

### Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

## Features

- symptom tracking 
- Daily health summaries using OpenAI
- Patient data visualization
- AI-powered risk prediction
