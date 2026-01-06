"""
DATA_AGENT.PY - Input Normalization
Converts any input format to plain text
"""

from agno import Agent, Context


class DataAgent(Agent):
    name = "data_agent"

    def run(self, ctx: Context):
        """Convert input to raw text"""
        input_data = ctx.state.get("input")
        if not input_data:
            raise ValueError("No input provided")

        # Dict to text
        if isinstance(input_data, dict):
            raw_text = "\n".join(f"{k}: {v}" for k, v in input_data.items())
        else:
            raw_text = str(input_data)

        ctx.state["raw_text"] = raw_text.strip()