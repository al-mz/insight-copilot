# insight-copilot

## Introduction
A modular, open-source Co-Pilot app built with LangGraph and CopilotKit. InsightCopilot enables natural language querying and real-time data visualization for any structured dataset.

![insight-copilot](https://github.com/user-attachments/assets/6ed3e665-01d7-49b0-addc-5ae7abdc3ccf)

## Backend Setup

### Prerequisites
- Python 3.8+
- SQLite3
- UV package manager

### Installation
1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies using UV:
```bash
uv pip install -r backend/requirements.txt
```

### Database Setup
The backend uses SQLite with the Sakila sample database. The database file will be automatically created in `backend/data/sqlite-sakila.db` when you first run the application.

### Running the Backend
1. Start the FastAPI server:
```bash
uvicorn backend.app.main:app --reload
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Frontend Setup

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation
1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

### Running the Frontend
1. Start the development server:
```bash
npm run dev
# or
yarn dev
```

2. Access the application:
- Open http://localhost:3000 in your browser

### Development Features
- Hot reloading for instant feedback
- TypeScript support for type safety
- Tailwind CSS for styling
- CopilotKit integration for AI-powered features

## Development

### Project Structure
```
InsightCopilot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # Entry point for FastAPI
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── query.py     # Handles query endpoints
│   │   │   └── insights.py  # Handles insights endpoints
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   └── database.py  # SQLite connection and schema setup
│   │   ├── agent/
│   │   │   ├── __init__.py
│   │   │   ├── configuration.py  # Agent configuration settings
│   │   │   ├── graph.py         # LangGraph workflow definition
│   │   │   ├── langgraph.json   # LangGraph configuration
│   │   │   ├── prompts.py       # Agent prompts and templates
│   │   │   ├── state.py         # State management for the agent
│   │   │   ├── tools.py         # Custom tools for the agent
│   │   │   └── utils.py         # Agent-specific utilities
│   │   └── utils/
│   │       └── helpers.py   # Utility functions (data processing, query generation, etc.)
│   ├── data/
│   │   └── sample_data.db   # Sample SQLite database
│   ├── tests/
│   │   ├── test_api.py      # API endpoint tests
│   │   └── test_langgraph.py # Agent logic tests
│   ├── uv.lock               # UV lock file for dependencies
│   └── pyproject.toml        # UV configuration and dependencies
│
├── frontend/
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx    # Real-time dashboard
│   │   │   ├── QueryInput.jsx   # Query input and response component
│   │   │   └── CopilotUI.jsx    # Copilot interface for interacting with LangGraph
│   │   ├── pages/
│   │   │   ├── index.jsx        # Entry point for the Copilot app
│   │   │   └── api/
│   │   │       └── query.js     # API route to communicate with FastAPI
│   │   ├── styles/
│   │   │   └── globals.css
│   │   └── utils/
│   │       └── apiClient.js     # Axios setup for API requests
│   └── package.json             # Frontend dependencies
│
├── .env.example                # Environment variable template
├── .gitignore                  # Ignored files
├── README.md                   # Project overview and setup instructions
├── docker-compose.yml          # Docker configuration for backend and frontend
├── LICENSE                     # Open-source license
└── Makefile                    # Common project commands (setup, run, test)
