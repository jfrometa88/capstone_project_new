
from common.utils.logger import setup_logger
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.plugins.base_plugin import BasePlugin

class MinimalTracingPlugin(BasePlugin):
    """Minimal tracing plugin. Logs agent and LLM invocations with basic stats."""

    def __init__(self) -> None:
        super().__init__(name="minimal_tracing_plugin")
        self.agent_count = 0
        self.llm_count = 0
        self.logger = setup_logger("minimal_tracing")

    async def before_agent_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext
    ) -> None:
        """Count and log agent runs."""
        self.agent_count += 1
        session_id = getattr(callback_context, 'session_id', 'unknown')
        
        self.logger.info(f"🔍 [TRACE] Agent '{agent.name}' started - "
                        f"Count: {self.agent_count} - Session: {session_id}")

    async def before_model_callback(
        self, *, callback_context: CallbackContext, llm_request: LlmRequest
    ) -> None:
        """Count and log LLM requests."""
        self.llm_count += 1
        model_name = getattr(llm_request, 'model_name', 'unknown')
        
        self.logger.info(f"🧠 [TRACE] LLM Request #{self.llm_count} - Model: {model_name}")

    def get_stats(self):
        """Get simple statistics."""
        return {
            "agent_invocations": self.agent_count,
            "llm_requests": self.llm_count
        }

# Global instance
tracing_plugin = MinimalTracingPlugin()