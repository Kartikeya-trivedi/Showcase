"""
SCHEMA_BUILDER.PY - Portfolio Schema Construction Agent

Transforms parsed resume data into structured portfolio schema.
Converted to Agno Agent pattern.
"""

from agno import Agent, Context
import logging

logger = logging.getLogger(__name__)


class SchemaBuilderAgent(Agent):
    """
    Agno Agent that builds portfolio schema from LLM-extracted profile data.
    
    INPUT (from ctx.state):
        - profile: dict with name, role, skills, experience_years, projects
    
    OUTPUT (to ctx.state):
        - schema: structured portfolio blueprint
    """
    
    name = "schema_builder_agent"

    def run(self, ctx: Context):
        """Build schema from profile data"""
        profile = ctx.state.get("profile")
        if not profile:
            raise ValueError("SchemaBuilderAgent: profile missing from context")

        logger.info(f"Building schema for profile: {profile.get('name', 'Unknown')}")
        
        schema = {
            "profile_summary": self._build_profile_summary(profile),
            "hero": self._build_hero_schema(profile),
            "bio": self._build_bio_schema(profile),
            "projects": self._build_projects_schema(profile),
            "skills": self._build_skills_schema(profile),
            "layout_hints": self._build_layout_hints(profile),
            "generation_flags": {
                "hero": True,
                "bio": True,
                "projects": True
            }
        }

        ctx.state["schema"] = schema
        logger.info("Schema built successfully")

    def _build_profile_summary(self, profile: dict) -> dict:
        """Extract high-level profile signals"""
        return {
            "name": profile.get("name"),
            "role": profile.get("role"),
            "experience_years": profile.get("experience_years", 0),
            "has_projects": bool(profile.get("projects")),
            "skill_count": len(profile.get("skills", []))
        }

    def _build_hero_schema(self, profile: dict) -> dict:
        """Build hero section schema"""
        role = profile.get("role", "Professional")
        exp = profile.get("experience_years", 0)
        
        tagline = f"{role}"
        if exp > 0:
            tagline += f" with {exp}+ years experience"

        return {
            "name": profile.get("name", "Portfolio"),
            "tagline": tagline,
            "contact": profile.get("contact", {})
        }

    def _build_bio_schema(self, profile: dict) -> dict:
        """Build bio section structure"""
        bio_points = []
        
        if profile.get("role"):
            bio_points.append(f"Role: {profile['role']}")
        
        if profile.get("experience_years"):
            bio_points.append(f"Experience: {profile['experience_years']} years")
        
        if profile.get("skills"):
            skills_preview = ", ".join(profile["skills"][:5])
            bio_points.append(f"Key skills: {skills_preview}")
        
        if profile.get("projects"):
            bio_points.append(f"Notable projects: {len(profile['projects'])}")

        return {
            "sections": ["introduction", "background", "highlights", "closing"],
            "reference_points": bio_points,
            "length_hint": "medium"
        }

    def _build_projects_schema(self, profile: dict) -> list:
        """Build projects schema"""
        projects = profile.get("projects", [])
        
        # If projects is a string or number, convert to basic list
        if isinstance(projects, (str, int)):
            return []
        
        result = []
        for idx, project in enumerate(projects):
            if isinstance(project, dict):
                result.append({
                    "id": f"project_{idx}",
                    "title": project.get("title", f"Project {idx + 1}"),
                    "description": project.get("description", ""),
                    "technologies": project.get("technologies", []),
                    "priority": "high" if idx < 3 else "normal"
                })
            elif isinstance(project, str):
                result.append({
                    "id": f"project_{idx}",
                    "title": project,
                    "description": "",
                    "technologies": [],
                    "priority": "high" if idx < 3 else "normal"
                })
        
        return result

    def _build_skills_schema(self, profile: dict) -> dict:
        """Build skills schema"""
        skills = profile.get("skills", [])
        
        # Basic categorization by common patterns
        categories = {
            "languages": [],
            "frameworks": [],
            "tools": [],
            "other": []
        }
        
        for skill in skills:
            skill_lower = skill.lower()
            if any(lang in skill_lower for lang in ["python", "javascript", "java", "c++", "go", "rust"]):
                categories["languages"].append(skill)
            elif any(fw in skill_lower for fw in ["react", "vue", "angular", "django", "flask", "spring"]):
                categories["frameworks"].append(skill)
            elif any(tool in skill_lower for tool in ["docker", "git", "aws", "kubernetes", "jenkins"]):
                categories["tools"].append(skill)
            else:
                categories["other"].append(skill)

        return {
            "raw": skills,
            "count": len(skills),
            "categories": {k: v for k, v in categories.items() if v}  # Only non-empty
        }

    def _build_layout_hints(self, profile: dict) -> dict:
        """Provide layout suggestions"""
        sections = ["hero", "bio", "skills"]
        
        if profile.get("projects"):
            sections.insert(2, "projects")
        
        exp = profile.get("experience_years", 0)
        density = "detailed" if exp >= 5 else "balanced"

        return {
            "sections": sections,
            "density": density,
            "emphasis": "projects" if profile.get("projects") else "skills"
        }