# An example of clinical decision-making dashboard

A web application for tracking symptoms and physiological data. 

## Prerequisites

- Node.js (v16 or higher)
- Python 3.8+
- MongoDB
- OpenAI API key
- Alexa Developer Account

## Environment Setup

### Backend Configuration

Create a `.env` file in the `backend` directory:

```env
MONGO_URI=mongodb://localhost:27017/your_database
OPENAI_API_KEY=your_openai_key_here
ALEXA_API_KEY=your_alexa_api_key_here
```

### Frontend Configuration

Create a `.env` file in the `frontend` directory:

```env
VITE_API_BASE_URL=http://localhost:5002
VITE_ALEXA_API_KEY=your_alexa_api_key_here
```

## Installation

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Unix/macOS
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Start the Flask server
python -m app.run
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Features

- symptom tracking 
- Daily health summaries using OpenAI
- Patient data visualization
- AI-powered risk prediction
