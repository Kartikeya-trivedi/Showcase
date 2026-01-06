"""
TEMPLATE_SELECTOR_AGENT.PY - Template Selection
Picks best template based on profile
"""

import json
from pathlib import Path
from agno import Agent, Context

TEMPLATE_ROOT = Path("showcase/app/templates")
REGISTRY_PATH = TEMPLATE_ROOT / "registry.json"


class TemplateSelectorAgent(Agent):
    name = "template_selector_agent"

    def run(self, ctx: Context):
        """Select template based on profile"""
        profile = ctx.state.get("profile")
        if not profile:
            raise ValueError("No profile found")

        # Load registry (with fallback)
        try:
            registry = self._load_registry()
        except:
            # Fallback: use default template
            ctx.state["template"] = {
                "id": "t01",
                "name": "default",
                "path": "default_template"
            }
            return

        # Select template
        template_id = self._select_template(profile, registry)
        meta = registry.get(template_id, registry.get("t01"))

        ctx.state["template"] = {
            "id": template_id,
            "name": meta["name"],
            "files": meta.get("files", []),
            "path": str(TEMPLATE_ROOT / f"{template_id}_{meta['name'].lower()}")
        }

    def _load_registry(self):
        """Load template registry"""
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _select_template(self, profile, registry):
        """Simple template selection logic"""
        role = profile.get("role", "").lower()
        exp = profile.get("experience_years", 0)

        # Selection logic
        if "senior" in role or exp >= 7:
            if "t03" in registry:
                return "t03"
        
        if "developer" in role or "engineer" in role:
            if "t02" in registry:
                return "t02"
        
        # Default
        return "t01"