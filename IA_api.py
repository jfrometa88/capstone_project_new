# [Nombre del programa, ej: Warehouse AI Agent]
# Copyright (C) [Año] [Tu Nombre Completo]
# 
# Este programa es software libre: usted puede redistribuirlo y/o modificarlo
# bajo los términos de la Licencia Pública General de GNU
# tal como la publica la Free Software Foundation, ya sea la versión 3
# de la Licencia, o (a su elección) cualquier versión posterior.
#
# Este programa se distribuye con la esperanza de que sea útil,
# pero SIN NINGUNA GARANTÍA; incluso sin la garantía implícita de
# COMERCIALIZACIÓN o IDONEIDAD PARA UN PROPÓSITO PARTICULAR. 
# Consulte la Licencia Pública General de GNU para más detalles.
#
# Debería haber recibido una copia de la Licencia Pública General de GNU
# junto con este programa. Si no, vea <https://www.gnu.org/licenses/>.

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from utils.logger import setup_logger
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent_manager import agent_manager

# Configure logging
logger = setup_logger()

# Create FastAPI app
app = FastAPI(
    title="Warehouse AI Agent API",
    description="API for Warehouse Analytics AI Agents",
    version="1.0.0"
)

# CORS middleware to allow Dash frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8050", "http://127.0.0.1:8050"],  # Dash default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class AgentQuery(BaseModel):
    message: str
    session_id: str = "default_session"

# Response model
class AgentResponse(BaseModel):
    response: str
    status: str
    session_id: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Warehouse AI Agent API"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agents_initialized": agent_manager._initialized,
        "service": "Warehouse AI Agent API"
    }

@app.post("/query", response_model=AgentResponse)
async def query_agent(query: AgentQuery):
    """
    Send a query to the AI agent and get response
    """
    try:
        logger.info(f"Received query: {query.message}")
        
        response = await agent_manager.query_orchestrator(
            user_message=query.message,
            session_id=query.session_id
        )
        
        return AgentResponse(
            response=response,
            status="success",
            session_id=query.session_id
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/agents")
async def get_agents_info():
    """Get information about available agents"""
    return {
        "orchestrator_agent": "Main agent that routes to specialized agents",
        "specialized_agents": [
            "client_service_agent - Client service level analysis",
            "reference_expeditions_agent - Demand and forecasting analysis",
            "stock_analysis_agent - Stock and inventory analysis"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "IA_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload during development        
    )