import uvicorn
from copilotkit import CopilotKitRemoteEndpoint, LangGraphAgent
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .agent.graph import graph
from .api import insights
from .db.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="InsightCopilot API", description="API for extracting insights from the Sakila database", version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize CopilotKit SDK
sdk = CopilotKitRemoteEndpoint(
    agents=[
        LangGraphAgent(
            name="insight_copilot_agent",
            description="A copilot agent that can extract insights from the Sakila database",
            graph=graph,
        )
    ],
)

# Add CopilotKit endpoint
add_fastapi_endpoint(app, sdk, "/copilotkit", use_thread_pool=False)

# Include routers
app.include_router(insights.router, prefix="/api/v1", tags=["insights"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to InsightCopilot API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "endpoints": {
            "insights": {
                "top_films": "/api/v1/insights/top-films",
                "category_performance": "/api/v1/insights/category-performance",
                "customer_activity": "/api/v1/insights/customer-activity",
                "store_performance": "/api/v1/insights/store-performance",
                "actor_popularity": "/api/v1/insights/actor-popularity",
            }
        },
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
