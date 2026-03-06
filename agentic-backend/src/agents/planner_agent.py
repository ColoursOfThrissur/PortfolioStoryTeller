"""
Planner Agent - The brain that orchestrates report generation
Uses Gemini 2.5 Flash to interpret vague prompts and guide users
"""
import os
import json
from typing import Dict, Optional, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from core.report_schema import REPORT_SCHEMA, get_next_step, get_required_inputs, get_missing_dependencies
from core.state_manager import WorkflowState
from core.tool_registry import get_tools_for_section


class PlannerAgent:
    """
    Planner Agent - Interprets user intent and orchestrates workflow
    
    Responsibilities:
    - Parse vague user prompts
    - Determine current step in workflow
    - Identify missing inputs
    - Guide user with clarifying questions
    - Route to appropriate section agent
    """
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.3,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
    
    async def interpret_user_intent(self, user_message: str, state: WorkflowState) -> Dict:
        """
        Interpret what the user wants to do
        
        Returns:
            {
                "intent": "generate_report" | "generate_section" | "provide_data" | "question",
                "section_requested": "performance_summary" | None,
                "data_provided": {"client_name": "John", ...} | None,
                "needs_clarification": True | False,
                "clarification_question": "..." | None
            }
        """
        
        system_prompt = f"""You are a financial report planning assistant. Your job is to understand what the user wants to do.

REPORT STRUCTURE:
{json.dumps(REPORT_SCHEMA, indent=2)}

CURRENT STATE:
{state.get_context_summary()}

TASK:
Analyze the user's message and determine their intent. Return a JSON object with:
- intent: "generate_report" (full report), "generate_section" (specific section), "provide_data" (uploading file/info), "skip_section" (skip current), or "question" (asking about process)
- section_requested: name of section if specific (e.g., "performance_summary", "allocation_overview", "holdings_detail", "market_commentary", "activity_summary", "planning_notes") or null
- data_provided: any data mentioned (client_name, period, benchmark, etc.) or null
- needs_clarification: true if you need more info
- clarification_question: what to ask user if needs_clarification is true

USER CAN ASK FOR SPECIFIC SECTIONS:
- "show me allocation" → section_requested: "allocation_overview"
- "what are my holdings" → section_requested: "holdings_detail"
- "give me market commentary" → section_requested: "market_commentary"
- "skip this" → intent: "skip_section"
- "continue" or "next" → intent: "generate_report" (continue sequential)

EXAMPLES:
User: "Generate Q4 2025 report for John Mitchell"
{{
  "intent": "generate_report",
  "section_requested": null,
  "data_provided": {{"client_name": "John Mitchell", "period": "Q4-2025"}},
  "needs_clarification": true,
  "clarification_question": "Please upload the portfolio file to begin."
}}

User: "Show me the allocation breakdown"
{{
  "intent": "generate_section",
  "section_requested": "allocation_overview",
  "data_provided": null,
  "needs_clarification": false,
  "clarification_question": null
}}

User: "Skip activity summary"
{{
  "intent": "skip_section",
  "section_requested": "activity_summary",
  "data_provided": null,
  "needs_clarification": false,
  "clarification_question": null
}}

Return ONLY valid JSON, no other text."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            # Extract JSON from response
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            
            return json.loads(content)
        except Exception as e:
            # Fallback
            return {
                "intent": "question",
                "section_requested": None,
                "data_provided": None,
                "needs_clarification": True,
                "clarification_question": "I didn't understand. Could you rephrase?"
            }
    
    async def plan_next_action(self, state: WorkflowState) -> Dict:
        """
        Determine what should happen next based on current state
        
        Returns:
            {
                "action": "request_input" | "execute_section" | "complete",
                "section": step_number | None,
                "missing_inputs": [...],
                "message": "User-facing message"
            }
        """
        
        # Check if all steps complete
        if len(state.completed_steps) == REPORT_SCHEMA["total_steps"]:
            return {
                "action": "complete",
                "section": None,
                "missing_inputs": [],
                "message": "All sections complete! Ready to generate final PDF report."
            }
        
        # Get next step
        next_step = get_next_step(state.completed_steps)
        
        if not next_step:
            return {
                "action": "error",
                "section": None,
                "missing_inputs": [],
                "message": "Unable to determine next step. Please contact support."
            }
        
        step_num = next_step["step_number"]
        step_name = next_step["name"]
        
        # Check required inputs
        required = get_required_inputs(step_num)
        missing = []
        
        for req in required["required"]:
            if req not in state.collected_data:
                missing.append(req)
        
        if missing:
            # Need to request inputs
            state.set_missing_inputs(missing)
            
            # Generate user-friendly message
            message = await self._generate_input_request_message(step_name, missing, state)
            
            return {
                "action": "request_input",
                "section": step_num,
                "missing_inputs": missing,
                "message": message
            }
        else:
            # Ready to execute section
            tools_needed = get_tools_for_section(step_name)
            
            return {
                "action": "execute_section",
                "section": step_num,
                "missing_inputs": [],
                "message": f"Generating {next_step['title']}...",
                "tools": tools_needed
            }
    
    async def _generate_input_request_message(self, section_name: str, missing_inputs: List[str], state: WorkflowState) -> str:
        """Generate friendly message asking for missing inputs"""
        
        system_prompt = f"""You are a helpful financial assistant. Generate a friendly, conversational message asking the user for missing information.

SECTION: {section_name}
MISSING INPUTS: {', '.join(missing_inputs)}

CURRENT DATA: {json.dumps(state.collected_data, indent=2)}

Generate a short, friendly message (1-2 sentences) asking for the missing information. Be specific about what format is needed.

Examples:
- "Please upload your portfolio file (Excel or CSV format) to get started."
- "I need the reporting period. For example: Q4-2025, or a custom date range like 2025-10-01 to 2025-12-31."
- "Which benchmark would you like to use? (Default is S&P 500 / ^GSPC)"

Return ONLY the message text, no JSON."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Generate request message for: {', '.join(missing_inputs)}")
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content.strip()
    
    async def route_to_agent(self, section_number: int, state: WorkflowState) -> str:
        """
        Determine which section agent to use
        
        Returns:
            Agent class name (e.g., "PerformanceAgent")
        """
        step_config = REPORT_SCHEMA["steps"][section_number]
        return step_config["agent_class"]
    
    async def generate_progress_update(self, state: WorkflowState) -> str:
        """Generate progress summary for user"""
        
        total = REPORT_SCHEMA["total_steps"]
        completed = len(state.completed_steps)
        
        progress_pct = (completed / total) * 100
        
        completed_names = []
        for step_num in state.completed_steps:
            step_config = REPORT_SCHEMA["steps"][step_num]
            completed_names.append(step_config["title"])
        
        message = f"Progress: {completed}/{total} sections complete ({progress_pct:.0f}%)\n\n"
        message += "Completed:\n"
        for name in completed_names:
            message += f"  ✓ {name}\n"
        
        next_step = get_next_step(state.completed_steps)
        if next_step:
            message += f"\nNext: {next_step['title']}"
        
        return message
