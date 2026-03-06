"""
Test script for agentic backend - verify all agents work
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agents.parameters_agent import ParametersAgent
from agents.performance_agent import PerformanceAgent
from agents.allocation_agent import AllocationAgent
from agents.holdings_agent import HoldingsAgent
from agents.commentary_agent import CommentaryAgent
from agents.activity_agent import ActivityAgent
from agents.planning_agent import PlanningAgent
from agents.output_agent import OutputAgent


async def test_full_workflow():
    """Test complete workflow through all 8 steps"""
    
    print("=" * 60)
    print("TESTING AGENTIC BACKEND - ALL 8 STEPS")
    print("=" * 60)
    
    # Step 1: Parameters
    print("\n[Step 1] Testing Parameters Agent...")
    params_agent = ParametersAgent()
    
    test_file = Path(__file__).parent.parent / "input" / "portfolios" / "john_mitchell_q4_2025.xlsx"
    
    params_result = await params_agent.execute({
        "client_name": "John Mitchell",
        "period": "Q4-2025",
        "portfolio_file": str(test_file.absolute())
    })
    
    if params_result["status"] == "complete":
        print(f"✅ Parameters collected: {params_result['parameters']['client_name']}")
        print(f"   Holdings: {len(params_result['parameters']['holdings'])}")
        print(f"   Period: {params_result['parameters']['period']['name']}")
    else:
        print(f"❌ Failed: {params_result.get('error')}")
        return
    
    # Prepare state data
    state_data = params_result['parameters']
    section_results = {}
    
    # Step 2: Performance
    print("\n[Step 2] Testing Performance Agent...")
    perf_agent = PerformanceAgent()
    await perf_agent.initialize()
    
    try:
        perf_result = await perf_agent.generate(
            {
                "client_name": state_data["client_name"],
                "holdings": state_data["holdings"]
            },
            state_data["period"]
        )
        
        if perf_result["status"] == "complete":
            print(f"✅ Performance calculated")
            print(f"   QTD Return: {perf_result['metrics']['portfolio_return']:.2f}%")
            print(f"   Benchmark: {perf_result['metrics']['benchmark_return']:.2f}%")
            section_results["performance_summary"] = perf_result
        else:
            print(f"❌ Failed: {perf_result.get('error')}")
    finally:
        await perf_agent.cleanup()
    
    # Step 3: Allocation
    print("\n[Step 3] Testing Allocation Agent...")
    alloc_agent = AllocationAgent()
    
    alloc_result = await alloc_agent.execute(state_data)
    
    if alloc_result["status"] == "complete":
        print(f"✅ Allocation calculated")
        print(f"   Total Value: ${alloc_result['total_value']:,.0f}")
        print(f"   Sectors: {len(alloc_result['allocation_table'])}")
        section_results["allocation_overview"] = alloc_result
    else:
        print(f"❌ Failed: {alloc_result.get('error')}")
    
    # Step 4: Holdings
    print("\n[Step 4] Testing Holdings Agent...")
    holdings_agent = HoldingsAgent()
    
    holdings_result = await holdings_agent.execute(state_data)
    
    if holdings_result["status"] == "complete":
        print(f"✅ Holdings detail generated")
        print(f"   Positions: {holdings_result['total_positions']}")
        print(f"   Total Value: ${holdings_result['total_value']:,.0f}")
        section_results["holdings_detail"] = holdings_result
    else:
        print(f"❌ Failed: {holdings_result.get('error')}")
    
    # Step 5: Commentary
    print("\n[Step 5] Testing Commentary Agent...")
    commentary_agent = CommentaryAgent()
    
    state_with_results = {**state_data, "section_results": section_results}
    commentary_result = await commentary_agent.execute(state_with_results)
    
    if commentary_result["status"] == "complete":
        print(f"✅ Commentary generated")
        print(f"   Market Summary: {commentary_result['market_summary'][:80]}...")
        section_results["market_commentary"] = commentary_result
    else:
        print(f"❌ Failed: {commentary_result.get('error')}")
    
    # Step 6: Activity
    print("\n[Step 6] Testing Activity Agent...")
    activity_agent = ActivityAgent()
    
    activity_result = await activity_agent.execute(state_data)
    
    if activity_result["status"] == "complete":
        print(f"✅ Activity summary generated")
        print(f"   {activity_result['summary']}")
        section_results["activity_summary"] = activity_result
    else:
        print(f"❌ Failed: {activity_result.get('error')}")
    
    # Step 7: Planning
    print("\n[Step 7] Testing Planning Agent...")
    planning_agent = PlanningAgent()
    
    planning_result = await planning_agent.execute(state_with_results)
    
    if planning_result["status"] == "complete":
        print(f"✅ Planning notes generated")
        print(f"   Recommendations: {planning_result['recommendations'][:80]}...")
        section_results["planning_notes"] = planning_result
    else:
        print(f"❌ Failed: {planning_result.get('error')}")
    
    # Step 8: Output
    print("\n[Step 8] Testing Output Agent...")
    output_agent = OutputAgent()
    
    final_state = {**state_data, "section_results": section_results}
    output_result = await output_agent.execute(final_state)
    
    if output_result["status"] == "complete":
        print(f"✅ Report assembled")
        print(f"   {output_result['message']}")
        print(f"   Sections: {output_result['report']['total_sections']}")
    else:
        print(f"❌ Failed: {output_result.get('error')}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print(f"\nCompleted Sections: {len(section_results)}/8")
    print(f"Section Names: {', '.join(section_results.keys())}")


if __name__ == "__main__":
    asyncio.run(test_full_workflow())
