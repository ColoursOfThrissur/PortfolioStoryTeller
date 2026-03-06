"""
State Manager - Maintains workflow state across chat interactions
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class WorkflowState:
    """Manages state for a single report generation session"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        
        # Workflow tracking
        self.report_type = "client_report"
        self.completed_steps = []
        self.current_step = None
        self.failed_steps = []
        
        # Collected data
        self.collected_data = {}
        self.missing_inputs = []
        
        # Section results
        self.section_results = {}
        
        # Chat context
        self.chat_history = []
        self.user_preferences = {}
    
    def update_step(self, step_number: int, status: str):
        """Update step status"""
        self.current_step = step_number
        self.updated_at = datetime.now().isoformat()
        
        if status == "completed" and step_number not in self.completed_steps:
            self.completed_steps.append(step_number)
        elif status == "failed" and step_number not in self.failed_steps:
            self.failed_steps.append(step_number)
    
    def add_data(self, key: str, value: Any):
        """Add collected data"""
        self.collected_data[key] = value
        self.updated_at = datetime.now().isoformat()
        
        # Remove from missing inputs if present
        if key in self.missing_inputs:
            self.missing_inputs.remove(key)
    
    def add_section_result(self, section_name: str, result: Dict):
        """Store section result"""
        self.section_results[section_name] = result
        self.updated_at = datetime.now().isoformat()
    
    def set_missing_inputs(self, inputs: List[str]):
        """Set list of missing inputs"""
        self.missing_inputs = inputs
        self.updated_at = datetime.now().isoformat()
    
    def add_chat_message(self, role: str, content: str):
        """Add message to chat history"""
        self.chat_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_context_summary(self) -> str:
        """Get summary of current state for LLM context"""
        summary = f"""
WORKFLOW STATE:
- Session: {self.session_id}
- Report Type: {self.report_type}
- Completed Steps: {self.completed_steps}
- Current Step: {self.current_step}
- Missing Inputs: {self.missing_inputs}

COLLECTED DATA:
"""
        for key, value in self.collected_data.items():
            if isinstance(value, (list, dict)):
                summary += f"- {key}: [collected]\n"
            else:
                summary += f"- {key}: {value}\n"
        
        summary += f"\nCOMPLETED SECTIONS: {list(self.section_results.keys())}"
        
        return summary
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "report_type": self.report_type,
            "completed_steps": self.completed_steps,
            "current_step": self.current_step,
            "failed_steps": self.failed_steps,
            "collected_data": self.collected_data,
            "missing_inputs": self.missing_inputs,
            "section_results": self.section_results,
            "chat_history": self.chat_history,
            "user_preferences": self.user_preferences
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary"""
        state = cls(data["session_id"])
        state.created_at = data["created_at"]
        state.updated_at = data["updated_at"]
        state.report_type = data["report_type"]
        state.completed_steps = data["completed_steps"]
        state.current_step = data["current_step"]
        state.failed_steps = data["failed_steps"]
        state.collected_data = data["collected_data"]
        state.missing_inputs = data["missing_inputs"]
        state.section_results = data["section_results"]
        state.chat_history = data["chat_history"]
        state.user_preferences = data["user_preferences"]
        return state


class StateManager:
    """Manages multiple workflow states (in-memory for MVP, can be Redis later)"""
    
    def __init__(self):
        self.states: Dict[str, WorkflowState] = {}
    
    def create_session(self, session_id: str) -> WorkflowState:
        """Create new session"""
        state = WorkflowState(session_id)
        self.states[session_id] = state
        return state
    
    def get_session(self, session_id: str) -> Optional[WorkflowState]:
        """Get existing session"""
        return self.states.get(session_id)
    
    def get_or_create_session(self, session_id: str) -> WorkflowState:
        """Get existing or create new session"""
        if session_id not in self.states:
            return self.create_session(session_id)
        return self.states[session_id]
    
    def delete_session(self, session_id: str):
        """Delete session"""
        if session_id in self.states:
            del self.states[session_id]
    
    def list_sessions(self) -> List[str]:
        """List all session IDs"""
        return list(self.states.keys())


# Global state manager instance
state_manager = StateManager()
