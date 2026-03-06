"""
Commentary Agent - Step 5: Market commentary
"""
import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage


class CommentaryAgent:
    """Step 5: Market Commentary"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
    
    async def execute(self, state_data: Dict) -> Dict:
        """Generate market commentary"""
        try:
            holdings = state_data.get("holdings", [])
            period = state_data.get("period", {})
            section_results = state_data.get("section_results", {})
            
            performance_data = section_results.get("performance_summary", {})
            allocation_data = section_results.get("allocation_overview", {})
            
            portfolio_return = performance_data.get('metrics', {}).get('portfolio_return', 0)
            benchmark_return = performance_data.get('metrics', {}).get('benchmark_return', 0)
            
            # Get top sectors
            sectors = allocation_data.get('sector_breakdown', {})
            top_sector = max(sectors.items(), key=lambda x: x[1])[0] if sectors else "Technology"
            
            # Generate commentary using Gemini
            commentary = await self._generate_commentary(
                period['name'],
                portfolio_return,
                benchmark_return,
                holdings,
                top_sector
            )
            
            return {
                "status": "complete",
                "section": "market_commentary",
                "commentary": commentary['full'],
                "market_summary": commentary['market_summary'],
                "portfolio_impact": commentary['portfolio_impact'],
                "outlook": commentary['outlook']
            }
            
        except Exception as e:
            import traceback
            return {
                "status": "error",
                "error": f"{str(e)}\n{traceback.format_exc()}"
            }
    
    async def _generate_commentary(self, period: str, portfolio_return: float, 
                                   benchmark_return: float, holdings: list, top_sector: str) -> Dict:
        """Generate AI commentary"""
        
        tickers = [h['ticker'] for h in holdings[:5]]
        
        messages = [
            SystemMessage(content="You are a professional financial advisor writing market commentary for a client report."),
            HumanMessage(content=f"""
Write a professional market commentary for {period}:

Portfolio Performance: {portfolio_return:.2f}%
Benchmark Performance: {benchmark_return:.2f}%
Top Holdings: {', '.join(tickers)}
Largest Sector: {top_sector}

Provide 3 sections (2-3 sentences each):

1. Market Summary: What happened in markets this quarter
2. Portfolio Impact: How it affected this portfolio
3. Outlook: Forward-looking positioning rationale

Keep it professional but accessible. No jargon.
""")
        ]
        
        response = await self.llm.ainvoke(messages)
        content = response.content
        
        # Parse sections
        lines = content.split('\n\n')
        
        market_summary = ""
        portfolio_impact = ""
        outlook = ""
        
        for line in lines:
            if 'market' in line.lower() and not market_summary:
                market_summary = line.replace('1. Market Summary:', '').replace('**Market Summary:**', '').strip()
            elif 'portfolio' in line.lower() and not portfolio_impact:
                portfolio_impact = line.replace('2. Portfolio Impact:', '').replace('**Portfolio Impact:**', '').strip()
            elif 'outlook' in line.lower() and not outlook:
                outlook = line.replace('3. Outlook:', '').replace('**Outlook:**', '').strip()
        
        # Fallback if parsing fails
        if not market_summary:
            market_summary = content[:200]
        if not portfolio_impact:
            portfolio_impact = f"The portfolio returned {portfolio_return:.2f}% during {period}."
        if not outlook:
            outlook = "We continue to monitor market conditions and maintain a diversified approach."
        
        return {
            'full': content,
            'market_summary': market_summary,
            'portfolio_impact': portfolio_impact,
            'outlook': outlook
        }
