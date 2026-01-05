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

from typing import Optional
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import sys
from pathlib import Path
from collections import deque

# Obtiene la ruta de la carpeta donde está este archivo
current_dir = Path(__file__).resolve().parent

# Obtiene la raíz del proyecto (un nivel arriba)
project_root = current_dir.parent

# Insertar en sys.path si no está
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from common.utils.logger import setup_logger

from agents.agent_manager import agent_manager

from agents.tracing_plugin import tracing_plugin

# Configure logging
logger = setup_logger('api.IA_api')

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

@app.get("/trajectory")
async def get_all_trajectories():
    """Get trajectory data for all sessions"""
    return tracing_plugin.get_stats()

if __name__ == "__main__":
    uvicorn.run(
        "IA_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload during development        
    )

@app.get("/logs")
async def obtener_logs(lineas: Optional[int] = None):
    """
    Devuelve las últimas N líneas del archivo de log usando rutas agnósticas.
    """
    # 1. Definir la ruta usando la misma estructura que en setup_logger
    # Es recomendable que esta ruta venga de una variable global o config
    log_path = Path("common") / "data" / "logs" / "logs.log"
    
    # 2. Verificación de existencia multiplataforma
    if not log_path.exists():
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado en {log_path}")
    
    n_lineas = lineas or 50
    
    # 3. Lectura eficiente (usando deque para no cargar todo el archivo en RAM)
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            # deque con maxlen solo guarda las últimas N líneas, ahorrando memoria
            ultimas_lineas = deque(f, maxlen=n_lineas)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer el archivo: {str(e)}")
    
    separador = "\n" + "-"*50 + "\n"
    # Unimos las líneas (deque se comporta como una lista)
    contenido_limpio = separador.join([linea.strip() for linea in ultimas_lineas])
        
    return Response(content=contenido_limpio, media_type="text/plain")
