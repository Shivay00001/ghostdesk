import logging
import os
import datetime
from typing import List, Any
from jinja2 import Template
from .base import BaseSkill, SkillResult
from ..core.memory import MemoryManager

logger = logging.getLogger(__name__)

class CanvasSkill(BaseSkill):
    TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LocalMolt Dashboard</title>
        <style>
            body { font-family: sans-serif; background: #1a1a1a; color: #fff; padding: 20px; }
            .card { background: #2d2d2d; padding: 15px; margin-bottom: 20px; border-radius: 8px; }
            h1 { color: #00ff9d; }
            .log { font-family: monospace; color: #aaa; }
        </style>
    </head>
    <body>
        <h1>LocalMolt Canvas</h1>
        <div class="card">
            <h2>Status</h2>
            <p>Last Updated: {{ timestamp }}</p>
            <p>Agent Name: {{ agent_name }}</p>
        </div>
        
        <div class="card">
            <h2>Recent Activity</h2>
            {% for item in history %}
            <div class="log">
                <strong>{{ item.role }}:</strong> {{ item.content }}
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    """

    def __init__(self):
        super().__init__(
            name="Canvas",
            description="Renders a visual HTML dashboard"
        )
        self.memory = MemoryManager.get_instance()
        self.output_path = "dashboard.html"

    @property
    def actions(self) -> List[str]:
        return ["RENDER_CANVAS"]

    def execute(self, action: str, params: Any, context: Any = None) -> SkillResult:
        if action == "RENDER_CANVAS":
            try:
                history = self.memory.get_recent_history(limit=10)
                agent_name = self.memory.recall("agent_name") or "LocalMolt"
                
                t = Template(self.TEMPLATE)
                html = t.render(
                    timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    agent_name=agent_name,
                    history=history
                )
                
                with open(self.output_path, "w", encoding="utf-8") as f:
                    f.write(html)
                    
                abs_path = os.path.abspath(self.output_path)
                return SkillResult(success=True, message=f"Canvas rendered to {abs_path}")
            except Exception as e:
                return SkillResult(success=False, message=str(e))
                
        return SkillResult(success=False, message=f"Action {action} not supported")
