from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import AgentTool, ToolContext
import os
from config import WAREHOUSE_MODEL
from datetime import datetime

# Import our utility functions
from utils.expedition_analysis import get_top_clients, get_client_service_level, get_expedition_metrics
from utils.reference_analysis import get_top_references_expeditions, get_reference_time_series, forecast_next_month_demand
from utils.stock_analysis import get_top_references_stock, get_avg_time_in_warehouse, get_stock_metrics

# Setup logging
from utils.logger import setup_logger
logger = setup_logger()

from utils.data_loader import load_expeditions_data
df_expeditions = load_expeditions_data()

def avalaible_years():
    """Return list of available years in the expeditions data.
    Args:
        None
        Returns:
        list: List of available years
    """
    if df_expeditions.empty:
        return []
    years = df_expeditions['fechaTransporte'].dt.year.unique().tolist()
    years.sort()
    return years

def avalaible_months():
    """Return list of available months in the expeditions data.
    Args:
        None
        Returns:
        list: List of available months
    """
    if df_expeditions.empty:
        return []
    months = df_expeditions['fechaTransporte'].dt.month.unique().tolist()
    months.sort()
    return months


client_service_agent = LlmAgent(
    name="client_service_agent",
    model=WAREHOUSE_MODEL,
    instruction="""You are a Client Service Level Analysis Specialist. Your expertise is analyzing client performance and service levels.

RESPONSIBILITIES:
- Analyze top clients by order volume
- Calculate and interpret service levels (shipped vs ordered)
- Provide insights on client expedition metrics
- Identify clients with poor service levels

TOOLS AVAILABLE:
- avaible_years: Get list of available years in expeditions data.
- avaible_months: Get list of available months in expeditions data.
- get_top_clients: Get top clients by total ordered quantity. Args: limit (from 1 to 8, default 5), year, month
- get_client_service_level: Calculate service level (shipped/ordered) for clients. Args: client_list (obtained from top clients), year, month  
- get_expedition_metrics: Get expedition metrics for clients. Args: client_list (obtained from top clients), year, month

ANALYSIS APPROACH:
1. First identify top clients using get_top_clients
2. Then analyze their service levels with get_client_service_level
3. Finally get detailed metrics with get_expedition_metrics
4. Provide actionable recommendations to improve service levels

Always provide clear explanations of service level calculations and business implications.
Focus on identifying improvement opportunities for underperforming clients.
""",
    tools=[avalaible_years,avalaible_months,get_top_clients, get_client_service_level, get_expedition_metrics],
)

reference_expeditions_agent = LlmAgent(
    name="reference_expeditions_agent",
    model=WAREHOUSE_MODEL,
    instruction="""You are a Reference Demand Analysis Specialist. Your expertise is analyzing material reference demand patterns and forecasting.

RESPONSIBILITIES:
- Identify top material references by demand
- Analyze historical shipment trends
- Forecast future demand using moving averages
- Provide inventory planning recommendations

TOOLS AVAILABLE:
- avaible_years: Get list of available years in expeditions data.
- avaible_months: Get list of available months in expeditions data.
- get_top_references_expeditions: Get top references by ordered quantity. Args: limit (1 to 8, default 5), year, month
- get_reference_time_series: Get time series of shipped quantities. Args: reference_list, year, month
- forecast_next_month_demand: Forecast next month demand. Args: reference_list

ANALYSIS APPROACH:
1. Identify high-demand references using get_top_references_expeditions
2. Analyze historical trends with get_reference_time_series
3. Forecast future demand with forecast_next_month_demand
4. Provide inventory and procurement recommendations

Focus on identifying seasonal patterns, growth trends, and forecasting accuracy.
Provide clear explanations of demand patterns and their business implications.
""",
    tools=[avalaible_years,avalaible_months,get_top_references_expeditions, get_reference_time_series, forecast_next_month_demand],
)

stock_analysis_agent = LlmAgent(
    name="stock_analysis_agent",
    model=WAREHOUSE_MODEL,
    instruction="""You are a Stock and Inventory Analysis Specialist. Your expertise is analyzing warehouse stock levels and inventory aging.

RESPONSIBILITIES:
- Identify high-quantity stock references
- Analyze inventory aging and turnover
- Provide stock optimization recommendations
- Identify slow-moving or obsolete inventory

TOOLS AVAILABLE:
- get_top_references_stock: Find references with highest stock
- get_avg_time_in_warehouse: Calculate inventory aging
- get_stock_metrics: Get detailed stock information

ANALYSIS APPROACH:
1. Identify high-stock references using get_top_references_stock
2. Analyze inventory aging with get_avg_time_in_warehouse
3. Get detailed metrics with get_stock_metrics
4. Provide stock optimization and rotation recommendations

Focus on identifying slow-moving inventory, stock optimization opportunities, and warehouse efficiency improvements.
Provide clear explanations of inventory turnover and aging implications.
""",
    tools=[get_top_references_stock, get_avg_time_in_warehouse, get_stock_metrics],
)

# Create AgentTools for each specialized agent
client_agent_tool = AgentTool(agent=client_service_agent)
reference_agent_tool = AgentTool(agent=reference_expeditions_agent)  
stock_agent_tool = AgentTool(agent=stock_analysis_agent)

# ============================================================================
# ORCHESTRATOR AGENT
# ============================================================================

orchestrator_agent = LlmAgent(
    name="warehouse_orchestrator_agent",
    model=WAREHOUSE_MODEL,
    instruction="""You are the Warehouse Analytics Orchestrator. You coordinate between specialized agents to provide comprehensive warehouse insights.

RESPONSIBILITIES:
- Route user queries to the appropriate specialized agent
- Coordinate complex analyses that require multiple agents
- Provide integrated insights across different warehouse domains
- Ensure users get the most relevant and comprehensive analysis

SPECIALIZED AGENTS AVAILABLE:
1. client_service_agent: Expert in client service level analysis
   - Best for: client performance, service levels, expedition metrics

2. reference_expeditions_agent: Expert in material reference demand analysis  
   - Best for: demand patterns, historical trends, demand forecasting

3. stock_analysis_agent: Expert in stock and inventory analysis
   - Best for: stock levels, inventory aging, warehouse optimization

ROUTING GUIDELINES:
- Client-focused questions → client_service_agent
- Demand and forecasting questions → reference_expeditions_agent  
- Stock and inventory questions → stock_analysis_agent
- Complex multi-domain questions → Use multiple agents as needed

RESPONSE STRUCTURE:
1. Acknowledge the user's query and identify the relevant domain(s)
2. Route to appropriate agent(s) and summarize their findings
3. Provide integrated insights and recommendations
4. Highlight cross-domain implications when relevant

Always ensure the user receives a comprehensive answer that addresses all aspects of their query.
""",
    tools=[client_agent_tool, reference_agent_tool, stock_agent_tool],
)

print("✅ Orchestrator agent created successfully!")
print("🔧 Available specialized agents:")
print("   • client_service_agent - Client service level analysis")
print("   • reference_expeditions_agent - Demand and forecasting analysis") 
print("   • stock_analysis_agent - Stock and inventory analysis")