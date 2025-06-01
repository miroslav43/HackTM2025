"""
AI Agent Service - Integration with the Romanian Civic Information Assistant
"""

import os
import sys
import json
import time
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

# Setup logging
logger = logging.getLogger(__name__)

class AgentService:
    """Service class to integrate the AI Agent with the backend"""
    
    def __init__(self):
        self.agent = None
        self.agent_config_path = None
        self._setup_agent_path()
        self._initialize_agent()
    
    def _setup_agent_path(self):
        """Setup the path to the AI agent"""
        # Get the root directory (Site)
        current_dir = Path(__file__).resolve()
        root_dir = current_dir
        
        # Navigate up to find the Site directory
        while root_dir.name != "Site" and root_dir.parent != root_dir:
            root_dir = root_dir.parent
            
        if root_dir.name != "Site":
            raise Exception("Could not find Site directory")
            
        # Setup agent paths
        self.agent_src_path = root_dir / "AI" / "src"
        self.agent_config_path = self.agent_src_path / "agent_config.json"
        self.tools_path = self.agent_src_path / "tools"
        
        # Add to Python path
        if str(self.agent_src_path) not in sys.path:
            sys.path.insert(0, str(self.agent_src_path))
        if str(self.tools_path) not in sys.path:
            sys.path.insert(0, str(self.tools_path))
            
        logger.info(f"Agent paths setup: {self.agent_src_path}")
    
    def _initialize_agent(self):
        """Initialize the agent with proper imports"""
        try:
            # Import agent after path setup
            from agent import Agent
            self.Agent = Agent
            
            # Verify config file exists
            if not self.agent_config_path.exists():
                logger.warning(f"Agent config not found at {self.agent_config_path}")
                # Create default config if missing
                self._create_default_config()
            
            logger.info("Agent service initialized successfully")
            
        except ImportError as e:
            logger.error(f"Failed to import agent: {e}")
            raise Exception(f"Could not import AI agent: {e}")
    
    def _create_default_config(self):
        """Create a default agent configuration for API usage"""
        default_config = {
            "query_processing": {
                "use_robust_reformulation": True,
                "gemini_model": "gemini-2.0-flash",
                "gemini_temperature": 0.1,
                "gemini_max_tokens": 500
            },
            "timpark_payment": {
                "use_timpark_payment": True,
                "gemini_model": "gemini-2.5-flash-preview-05-20",
                "gemini_temperature": 0.1,
                "gemini_max_tokens": 1000,
                "output": {"save_to_file": False}
            },
            "web_search": {
                "city_hint": "timisoara",
                "use_perplexity": True,
                "perplexity_model": "sonar-reasoning-pro",
                "perplexity_temperature": 0.1,
                "perplexity_max_tokens": 10000,
                "search_context_size": "high",
                "search_date_range": {
                    "search_after_date": "1/1/2005",
                    "search_before_date": "5/30/2025"
                }
            },
            "trusted_sites_search": {
                "use_trusted_sites_search": True,
                "gemini_domain_selection": {
                    "gemini_temperature": 0.1,
                    "gemini_max_tokens": 2000,
                    "gemini_model": "gemini-2.5-flash-preview-05-20"
                },
                "perplexity_filtered_search": {
                    "perplexity_model": "sonar-reasoning-pro",
                    "perplexity_temperature": 0.1,
                    "perplexity_max_tokens": 10000,
                    "city_hint": "timisoara",
                    "search_context_size": "high",
                    "search_after_date": "1/1/2005",
                    "search_before_date": "5/30/2025"
                },
                "output": {"save_to_file": False}
            },
            "final_response_generation": {
                "use_final_response_generation": True,
                "gemini_model": "gemini-2.5-flash-preview-05-20",
                "gemini_temperature": 0.1,
                "gemini_max_tokens": 15000,
                "rag_context": {
                    "use_rag_context": True,
                    "rag_domains": ["dfmt.ro", "timpark.ro"],
                    "rag_context_path": "rag_context"
                },
                "output": {"save_to_file": False}
            },
            "output": {
                "save_to_file": False,
                "output_folder": "results/agent_results",
                "include_reformulated_query": False,
                "include_search_results": False,
                "file_naming": {
                    "use_config_name": False,
                    "include_timestamp": True
                }
            },
            "current_test": {
                "question": "",
                "config_name": "api_request"
            }
        }
        
        # Save default config
        with open(self.agent_config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Created default agent config at {self.agent_config_path}")
    
    def _merge_config(self, base_config: Dict[str, Any], custom_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Merge custom configuration with base configuration"""
        if not custom_config:
            return base_config
        
        merged = base_config.copy()
        
        def deep_merge(base: Dict, custom: Dict):
            for key, value in custom.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
        
        deep_merge(merged, custom_config)
        return merged
    
    async def process_query(
        self, 
        query: str, 
        custom_config: Optional[Dict[str, Any]] = None,
        config_name: str = "api_request"
    ) -> Dict[str, Any]:
        """
        Process a query using the AI agent
        
        Args:
            query: User's question
            custom_config: Optional custom configuration to override defaults
            config_name: Configuration name for identification
            
        Returns:
            Dictionary containing agent results and metadata
        """
        start_time = time.time()
        
        try:
            # Load base configuration
            with open(self.agent_config_path, 'r', encoding='utf-8') as f:
                base_config = json.load(f)
            
            # Merge with custom config if provided
            final_config = self._merge_config(base_config, custom_config)
            
            # Update the current test section
            final_config["current_test"]["question"] = query
            final_config["current_test"]["config_name"] = config_name
            
            # Disable file saving for API usage (we return data instead)
            final_config["output"]["save_to_file"] = False
            final_config["timpark_payment"]["output"]["save_to_file"] = False
            final_config["trusted_sites_search"]["output"]["save_to_file"] = False
            final_config["final_response_generation"]["output"]["save_to_file"] = False
            
            # Create temporary config file for this request
            temp_config_path = self.agent_src_path / f"temp_config_{int(time.time() * 1000)}.json"
            
            try:
                # Write temporary config
                with open(temp_config_path, 'w', encoding='utf-8') as f:
                    json.dump(final_config, f, indent=4, ensure_ascii=False)
                
                # Run agent in executor to avoid blocking
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, 
                    self._run_agent_sync, 
                    str(temp_config_path),
                    query,
                    config_name
                )
                
                processing_time = time.time() - start_time
                
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "reformulated_query": result.get("reformulated_query", ""),
                    "search_results": result.get("search_results", {}),
                    "timpark_executed": result.get("timpark_executed", False),
                    "tools_used": result.get("tools_used", []),
                    "processing_time": processing_time,
                    "config_used": config_name,
                    "timestamp": datetime.now().isoformat()
                }
                
            finally:
                # Clean up temporary config file
                if temp_config_path.exists():
                    temp_config_path.unlink()
                    
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            processing_time = time.time() - start_time
            
            return {
                "success": False,
                "error": str(e),
                "processing_time": processing_time,
                "config_used": config_name,
                "timestamp": datetime.now().isoformat()
            }
    
    def _run_agent_sync(self, config_path: str, query: str, config_name: str) -> Dict[str, Any]:
        """Run the agent synchronously (called from executor)"""
        try:
            # Create agent instance with temporary config
            agent = self.Agent(config_path)
            
            # Process the query
            result = agent.process_query(query, config_name)
            
            # Extract and structure the result
            tools_used = []
            timpark_executed = False
            response_text = ""
            reformulated_query = ""
            search_results = {}
            
            # Parse the result to extract information
            if isinstance(result, dict):
                # Check if this is the complex JSON structure from the agent
                if 'final_synthesized_response' in result:
                    # Extract the final synthesized response as the main response
                    response_text = result.get('final_synthesized_response', '')
                    
                    # Extract reformulated query
                    reformulated_query = result.get('reformulated_query', '')
                    
                    # Check for TimPark execution
                    timpark_result = result.get('timpark_payment_result', {})
                    if isinstance(timpark_result, dict):
                        timpark_executed = timpark_result.get('tool_activated', False)
                        if timpark_executed:
                            tools_used.append("timpark_payment")
                    
                    # Determine tools used based on available results
                    if reformulated_query:
                        tools_used.append("query_reformulation")
                    
                    if result.get('regular_web_search_result'):
                        tools_used.append("web_search")
                    
                    if result.get('trusted_sites_search_result'):
                        tools_used.append("trusted_sites_search")
                    
                    if result.get('final_synthesized_response'):
                        tools_used.append("final_response_generation")
                    
                    # Store search results for metadata
                    search_results = {
                        'web_search': bool(result.get('regular_web_search_result')),
                        'trusted_sites': bool(result.get('trusted_sites_search_result')),
                        'timpark_result': timpark_result
                    }
                    
                elif 'response' in result:
                    # Simple response format
                    response_text = result.get('response', str(result))
                    reformulated_query = result.get('reformulated_query', '')
                    search_results = result.get('search_results', {})
                else:
                    # Fallback - use the entire result as response
                    response_text = str(result)
                
                # Check for TimPark execution in the response text if not found above
                if not timpark_executed and ("parcarea a fost plătită cu succes" in response_text.lower() or 
                                           "payment completed" in response_text.lower() or
                                           "timpark" in response_text.lower()):
                    timpark_executed = True
                    if "timpark_payment" not in tools_used:
                        tools_used.append("timpark_payment")
                
            else:
                # Handle string response
                response_text = str(result)
            
            # Clean up the response text if needed
            if not response_text.strip():
                response_text = "Ne pare rău, nu am putut genera un răspuns pentru această întrebare."
            
            return {
                "response": response_text,
                "reformulated_query": reformulated_query,
                "search_results": search_results,
                "timpark_executed": timpark_executed,
                "tools_used": tools_used
            }
            
        except Exception as e:
            logger.error(f"Error in agent execution: {e}")
            raise e
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get the default agent configuration"""
        try:
            with open(self.agent_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate agent configuration structure"""
        required_sections = [
            "query_processing", "timpark_payment", "web_search", 
            "trusted_sites_search", "final_response_generation", "output"
        ]
        
        try:
            for section in required_sections:
                if section not in config:
                    logger.warning(f"Missing config section: {section}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Config validation error: {e}")
            return False
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get information about available agent tools"""
        return [
            {
                "name": "query_reformulation",
                "description": "Uses Gemini to enhance and reformulate user queries for better search results",
                "configurable": True
            },
            {
                "name": "timpark_payment",
                "description": "Automated parking payment for Timișoara with intent detection",
                "configurable": True
            },
            {
                "name": "web_search",
                "description": "Searches Romanian websites using Perplexity with geographic filtering",
                "configurable": True
            },
            {
                "name": "trusted_sites_search", 
                "description": "Searches only trusted Romanian government websites",
                "configurable": True
            },
            {
                "name": "final_response_generation",
                "description": "Synthesizes all search results into comprehensive final response with RAG context",
                "configurable": True
            }
        ]

# Global instance
agent_service = AgentService() 