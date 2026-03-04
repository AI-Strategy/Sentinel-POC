# .agent/skills/dbs_guard.py
from typing import List, Literal
from pydantic import BaseModel, Field

class DBSCheckInput(BaseModel):
    proposed_action: str = Field(..., description="The command or query to be executed.")
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(..., description="Estimated risk.")
    impact_scope: str = Field(..., description="What will be affected? (e.g., 'Production DB', 'Local File').")

async def run(input_data: DBSCheckInput) -> dict:
    """
    The 'Don't Be Stupid' Protocol Guard.
    Forces a pause and reflection step for HIGH/CRITICAL actions.
    """
    
    # 1. Immediate Auto-Reject for prohibited actions
    prohibited_substrings = ["rm -rf /", "DROP DATABASE", "FLUSHALL"]
    if any(s in input_data.proposed_action for s in prohibited_substrings):
        return {
            "approved": False, 
            "reason": "HARD_BLOCK: Detectable catastrophic command.",
            "better_way": "Use granular deletion or soft-delete."
        }

    # 2. Reflection Logic for High Risk
    if input_data.risk_level in ["HIGH", "CRITICAL"]:
        print(f"⚠️ DBS TRIGGERED: {input_data.proposed_action}")
        print(f"❓ REFLECTION: Is there a non-destructive way to do this?")
        
        # In a real agent, this would trigger a 'HumanApprovalRequest' event
        return {
            "approved": False,
            "status": "AWAITING_HUMAN_APPROVAL",
            "reflection_prompt": "Explain why a reversible alternative is impossible."
        }

    return {"approved": True, "status": "AUTO_LOGGED"}
