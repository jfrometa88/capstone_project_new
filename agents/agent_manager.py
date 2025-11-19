from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import logging
from .agent import orchestrator_agent, client_service_agent, reference_expeditions_agent, stock_analysis_agent

logger = logging.getLogger(__name__)

class WarehouseAgentManager:
    """Manager for all warehouse analytics AI agents"""
    
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.orchestrator = orchestrator_agent
        self.APP_NAME = "agents"
        self.runner = Runner(agent=self.orchestrator, app_name=self.APP_NAME, session_service=self.session_service)
        self.specialized_agents = {
            'client': client_service_agent,
            'reference': reference_expeditions_agent, 
            'stock': stock_analysis_agent
        }
        
    async def query_orchestrator(self, user_message, session_id="default_session", USER_ID="default_user"):
        """
        Send query to orchestrator agent (recommended for most queries)
        """
        try:
            if type(user_message) == str:
                user_message = [user_message]
                for query in user_message:
                    logger.info(f"Orchestrator processing query: {query}")
                    # Convert the query string to the ADK Content format
                    query = types.Content(role="user", parts=[types.Part(text=query)])
            
            session = await self.session_service.get_session(
                app_name=self.APP_NAME,
                user_id=USER_ID,
                session_id=session_id
            )
            if not session:
                logger.info(f"Failed to retrieve session: {session_id}")
                session = await self.session_service.create_session(
                app_name=self.APP_NAME, 
                user_id=USER_ID, 
                session_id=session_id
            )
            
            async for event in self.runner.run_async(
                user_id=USER_ID, 
                session_id=session.id, 
                new_message=query
            ):
                # Check if the event contains valid content
                if event.content and event.content.parts:
                    # Filter out empty or "None" responses before printing
                    if (
                        event.content.parts[0].text != "None"
                        and event.content.parts[0].text
                    ):
                        response = event.content.parts[0].text
            
            return response if response else "No response generated"
            
        except Exception as e:
            logger.error(f"Error in orchestrator query: {e}")
            return f"I encountered an error: {str(e)}"
    
    
    
    def get_agent_descriptions(self):
        """Get descriptions of all available agents"""
        return {
            'orchestrator': 'Main agent that routes to specialized agents - recommended for most queries',
            'client_service': 'Specialized in client service level analysis',
            'reference_expeditions': 'Specialized in demand patterns and forecasting', 
            'stock_analysis': 'Specialized in stock levels and inventory aging'
        }

# Singleton instance
agent_manager = WarehouseAgentManager()