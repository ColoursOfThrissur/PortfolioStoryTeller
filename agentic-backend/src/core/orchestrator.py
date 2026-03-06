"""
Report Orchestrator - Main coordinator for agentic report generation
"""
import uuid
from typing import Dict, Optional
from datetime import datetime

from core.state_manager import state_manager, WorkflowState
from core.report_schema import REPORT_SCHEMA
from agents.planner_agent import PlannerAgent
from agents.parameters_agent import ParametersAgent
from agents.performance_agent import PerformanceAgent
from agents.allocation_agent import AllocationAgent
from agents.holdings_agent import HoldingsAgent
from agents.commentary_agent import CommentaryAgent
from agents.activity_agent import ActivityAgent
from agents.planning_agent import PlanningAgent
from agents.output_agent import OutputAgent


class ReportOrchestrator:
    """
    Main orchestrator that coordinates:
    - Planner Agent (interprets intent, plans next action)
    - State Manager (tracks progress)
    - Section Agents (execute specific sections)
    """
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.agents = {
            "ParametersAgent": ParametersAgent(),
            "PerformanceAgent": PerformanceAgent(),
            "AllocationAgent": AllocationAgent(),
            "HoldingsAgent": HoldingsAgent(),
            "CommentaryAgent": CommentaryAgent(),
            "ActivityAgent": ActivityAgent(),
            "PlanningAgent": PlanningAgent(),
            "OutputAgent": OutputAgent()
        }
    
    async def handle_message(self, session_id: str, user_message: str, uploaded_file: Optional[str] = None) -> Dict:
        """
        Main entry point - handle user message
        
        Args:
            session_id: Unique session identifier
            user_message: User's chat message
            uploaded_file: Path to uploaded file (if any)
        
        Returns:
            {
                "type": "response" | "status" | "result" | "error",
                "message": "...",
                "data": {...},
                "progress": {...}
            }
        """
        
        # Get or create session state
        state = state_manager.get_or_create_session(session_id)
        state.add_chat_message("user", user_message)
        
        try:
            # If file uploaded, add to collected data with absolute path
            if uploaded_file:
                from pathlib import Path
                file_path = Path(uploaded_file)
                if not file_path.is_absolute():
                    # If relative, make it absolute from current directory
                    file_path = Path.cwd() / file_path
                abs_path = str(file_path.absolute())
                print(f"[DEBUG] Orchestrator: File uploaded - {abs_path}")
                print(f"[DEBUG] File exists: {file_path.exists()}")
                state.add_data("portfolio_file", abs_path)
            
            # Step 1: Interpret user intent
            intent = await self.planner.interpret_user_intent(user_message, state)
            
            # Step 2: Update state with any provided data (but don't overwrite portfolio_file if already set)
            if intent.get("data_provided"):
                for key, value in intent["data_provided"].items():
                    # Don't overwrite portfolio_file if we already have the full path from upload
                    if key == "portfolio_file" and "portfolio_file" in state.collected_data:
                        continue
                    state.add_data(key, value)
            
            # Step 2.5: Check if we just got a file upload without explicit data
            if uploaded_file and "portfolio_file" not in state.collected_data:
                print(f"[DEBUG] Adding uploaded file to state: {uploaded_file}")
                state.add_data("portfolio_file", uploaded_file)
            
            # Step 3: Check if clarification needed
            if intent.get("needs_clarification"):
                response = {
                    "type": "response",
                    "message": intent["clarification_question"],
                    "progress": self._get_progress(state)
                }
                state.add_chat_message("assistant", intent["clarification_question"])
                return response
            
            # Step 4: Plan next action
            plan = await self.planner.plan_next_action(state)
            
            if plan["action"] == "request_input":
                # Need more data from user
                response = {
                    "type": "response",
                    "message": plan["message"],
                    "missing_inputs": plan["missing_inputs"],
                    "progress": self._get_progress(state)
                }
                state.add_chat_message("assistant", plan["message"])
                return response
            
            elif plan["action"] == "execute_section":
                # Ready to execute a section
                section_num = plan["section"]
                step_config = REPORT_SCHEMA["steps"][section_num]
                
                # Send status update
                status_msg = f"🤖 Generating {step_config['title']}..."
                state.add_chat_message("assistant", status_msg)
                
                # Execute section agent
                result = await self._execute_section(section_num, state)
                
                if result["status"] == "complete":
                    # Mark step as complete
                    state.update_step(section_num, "completed")
                    state.add_section_result(step_config["name"], result)
                    
                    # Generate success message
                    success_msg = f"✅ {step_config['title']} complete!"
                    
                    # Check if more sections needed
                    if len(state.completed_steps) < REPORT_SCHEMA["total_steps"]:
                        next_plan = await self.planner.plan_next_action(state)
                        if next_plan["action"] == "execute_section":
                            success_msg += f"\n\nNext: {REPORT_SCHEMA['steps'][next_plan['section']]['title']}"
                    
                    response = {
                        "type": "result",
                        "message": success_msg,
                        "section": step_config["name"],
                        "data": result,
                        "progress": self._get_progress(state)
                    }
                    state.add_chat_message("assistant", success_msg)
                    return response
                else:
                    # Section failed
                    state.update_step(section_num, "failed")
                    error_msg = f"❌ Failed to generate {step_config['title']}: {result.get('error', 'Unknown error')}"
                    
                    response = {
                        "type": "error",
                        "message": error_msg,
                        "error": result.get("error"),
                        "progress": self._get_progress(state)
                    }
                    state.add_chat_message("assistant", error_msg)
                    return response
            
            elif plan["action"] == "complete":
                # All sections done
                response = {
                    "type": "complete",
                    "message": "🎉 All sections complete! Ready to generate final PDF report.",
                    "progress": self._get_progress(state),
                    "sections": state.section_results
                }
                state.add_chat_message("assistant", response["message"])
                return response
            
            else:
                # Unknown action
                response = {
                    "type": "error",
                    "message": "Unable to determine next action. Please try again.",
                    "progress": self._get_progress(state)
                }
                return response
        
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            state.add_chat_message("assistant", error_msg)
            return {
                "type": "error",
                "message": error_msg,
                "error": str(e),
                "progress": self._get_progress(state)
            }
    
    async def _execute_section(self, section_number: int, state: WorkflowState) -> Dict:
        """Execute a specific section agent"""
        
        step_config = REPORT_SCHEMA["steps"][section_number]
        agent_class = step_config["agent_class"]
        
        if agent_class not in self.agents:
            return {
                "status": "error",
                "error": f"Agent {agent_class} not implemented yet"
            }
        
        agent = self.agents[agent_class]
        
        # Prepare data for agent - pass both collected_data and section_results
        state_data = {
            **state.collected_data,
            "section_results": state.section_results
        }
        
        # Execute based on section
        if section_number == 1:
            # Parameters agent
            result = await agent.execute(state.collected_data)
            
            # Store parameters in state
            if result["status"] == "complete":
                for key, value in result["parameters"].items():
                    state.add_data(key, value)
        
        elif section_number == 2:
            # Performance agent (special case - has different interface)
            await agent.initialize()
            try:
                portfolio_data = {
                    "client_name": state.collected_data.get("client_name"),
                    "holdings": state.collected_data.get("holdings", [])
                }
                period = state.collected_data.get("period", {})
                
                result = await agent.generate(portfolio_data, period)
            finally:
                await agent.cleanup()
        
        else:
            # All other agents (3-8) - pass full state
            result = await agent.execute(state_data)
        
        return result
    
    def _get_progress(self, state: WorkflowState) -> Dict:
        """Get progress summary"""
        total = REPORT_SCHEMA["total_steps"]
        completed = len(state.completed_steps)
        
        return {
            "total_steps": total,
            "completed_steps": completed,
            "percentage": int((completed / total) * 100),
            "current_step": state.current_step,
            "completed_sections": [
                REPORT_SCHEMA["steps"][num]["name"] 
                for num in state.completed_steps
            ]
        }
    
    async def get_session_status(self, session_id: str) -> Dict:
        """Get current session status"""
        state = state_manager.get_session(session_id)
        
        if not state:
            return {
                "exists": False,
                "message": "Session not found"
            }
        
        return {
            "exists": True,
            "session_id": session_id,
            "created_at": state.created_at,
            "progress": self._get_progress(state),
            "collected_data": {
                k: v for k, v in state.collected_data.items() 
                if k not in ["holdings", "portfolio_file"]  # Don't send large data
            },
            "missing_inputs": state.missing_inputs
        }
    
    def create_session(self) -> str:
        """Create new session and return ID"""
        session_id = str(uuid.uuid4())
        state_manager.create_session(session_id)
        return session_id


# Global orchestrator instance
orchestrator = ReportOrchestrator()
