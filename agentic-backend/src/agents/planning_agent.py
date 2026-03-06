"""
Planning Agent - Step 7: Planning notes and recommendations
"""
import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage


class PlanningAgent:
    """Step 7: Planning Notes"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.5,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
    
    async def execute(self, state_data: Dict) -> Dict:
        """Generate planning notes"""
        try:
            client_name = state_data.get("client_name", "Client")
            section_results = state_data.get("section_results", {})
            
            performance_data = section_results.get("performance_summary", {})
            allocation_data = section_results.get("allocation_overview", {})
            
            portfolio_return = performance_data.get('metrics', {}).get('portfolio_return', 0)
            total_value = allocation_data.get('total_value', 0)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                client_name,
                portfolio_return,
                total_value
            )
            
            return {
                "status": "complete",
                "section": "planning_notes",
                "recommendations": recommendations,
                "action_items": [
                    "Review portfolio allocation quarterly",
                    "Consider rebalancing if drift exceeds 5%",
                    "Schedule annual planning meeting"
                ],
                "next_review": "Next Quarter"
            }
            
        except Exception as e:
            import traceback
            return {
                "status": "error",
                "error": f"{str(e)}\n{traceback.format_exc()}"
            }
    
    async def _generate_recommendations(self, client_name: str, 
                                       portfolio_return: float, 
                                       total_value: float) -> str:
        """Generate AI recommendations"""
        
        messages = [
            SystemMessage(content="You are a financial advisor providing planning recommendations."),
            HumanMessage(content=f"""
Generate brief planning recommendations for {client_name}:

Portfolio Value: ${total_value:,.0f}
Recent Return: {portfolio_return:.2f}%

Provide 2-3 sentences covering:
- Progress assessment
- Any recommended actions
- Next steps

Keep it professional and actionable.
""")
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content
