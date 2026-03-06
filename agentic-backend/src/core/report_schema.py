"""
Report Schema - Defines the complete 8-step client report structure
"""

REPORT_SCHEMA = {
    "report_type": "client_report",
    "total_steps": 8,
    "steps": {
        1: {
            "name": "report_parameters",
            "title": "Report Parameters",
            "description": "Collect client info, reporting period, accounts, and benchmark",
            "depends_on": [],
            "required_inputs": ["client_name", "period", "portfolio_file"],
            "optional_inputs": ["benchmark", "accounts_filter", "firm_branding"],
            "agent_class": "ParametersAgent",
            "user_facing": True
        },
        2: {
            "name": "performance_summary",
            "title": "Performance Summary",
            "description": "Calculate household and account-level returns across multiple periods",
            "depends_on": [1],
            "required_data": ["holdings", "period", "benchmark"],
            "tools": ["fetch_historical_prices", "calculate_twr", "calculate_multi_period_returns"],
            "agent_class": "PerformanceAgent",
            "user_facing": True
        },
        3: {
            "name": "allocation_overview",
            "title": "Allocation Overview",
            "description": "Asset class breakdown with visual charts",
            "depends_on": [1, 2],
            "required_data": ["holdings", "current_prices"],
            "tools": ["fetch_current_prices", "calculate_allocation", "generate_pie_chart"],
            "agent_class": "AllocationAgent",
            "user_facing": True
        },
        4: {
            "name": "holdings_detail",
            "title": "Holdings Detail",
            "description": "Security-level data with returns and allocation",
            "depends_on": [1, 2, 3],
            "required_data": ["holdings", "current_prices", "period_returns"],
            "tools": ["fetch_company_profiles", "calculate_position_returns"],
            "agent_class": "HoldingsAgent",
            "user_facing": True
        },
        5: {
            "name": "market_commentary",
            "title": "Market Commentary",
            "description": "AI-generated market summary tailored to client sophistication",
            "depends_on": [1, 2],
            "required_data": ["holdings", "period", "performance_data"],
            "tools": ["fetch_market_news", "analyze_sentiment", "generate_narrative"],
            "agent_class": "CommentaryAgent",
            "user_facing": True
        },
        6: {
            "name": "activity_summary",
            "title": "Activity Summary",
            "description": "Trades, contributions, dividends, and fees during period",
            "depends_on": [1],
            "required_data": ["transactions", "period"],
            "optional_data": ["dividends", "fees"],
            "tools": ["parse_transactions", "calculate_dividends"],
            "agent_class": "ActivityAgent",
            "user_facing": True
        },
        7: {
            "name": "planning_notes",
            "title": "Planning Notes",
            "description": "Progress toward goals and recommendations",
            "depends_on": [1, 2],
            "required_data": ["performance_data"],
            "optional_data": ["client_goals", "risk_profile"],
            "tools": ["generate_recommendations"],
            "agent_class": "PlanningAgent",
            "user_facing": True
        },
        8: {
            "name": "output",
            "title": "Generate Report",
            "description": "Assemble all sections into PDF report",
            "depends_on": [1, 2, 3, 4, 5, 6, 7],
            "required_data": ["all_sections", "branding"],
            "tools": ["generate_pdf", "apply_branding"],
            "agent_class": "OutputAgent",
            "user_facing": True
        }
    }
}


def get_step_by_name(step_name: str) -> dict:
    """Get step configuration by name"""
    for step_num, step_config in REPORT_SCHEMA["steps"].items():
        if step_config["name"] == step_name:
            return {"step_number": step_num, **step_config}
    return None


def get_next_step(completed_steps: list) -> dict:
    """Determine next step based on completed steps"""
    for step_num in range(1, REPORT_SCHEMA["total_steps"] + 1):
        if step_num not in completed_steps:
            step_config = REPORT_SCHEMA["steps"][step_num]
            # Check if dependencies are met
            if all(dep in completed_steps for dep in step_config["depends_on"]):
                return {"step_number": step_num, **step_config}
    return None


def get_missing_dependencies(step_number: int, completed_steps: list) -> list:
    """Get list of missing dependencies for a step"""
    step_config = REPORT_SCHEMA["steps"][step_number]
    return [dep for dep in step_config["depends_on"] if dep not in completed_steps]


def get_required_inputs(step_number: int) -> dict:
    """Get required and optional inputs for a step"""
    step_config = REPORT_SCHEMA["steps"][step_number]
    return {
        "required": step_config.get("required_inputs", []) + step_config.get("required_data", []),
        "optional": step_config.get("optional_inputs", []) + step_config.get("optional_data", [])
    }
