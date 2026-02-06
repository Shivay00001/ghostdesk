import logging
import os
from typing import List, Any
from .base import BaseSkill, SkillResult

logger = logging.getLogger(__name__)

class FileSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="FileSystem",
            description="Reads and Writes files to the local disk"
        )
        # Sandbox to a specific workspace in real prod, but for Moltbot Local it's full access
        self.root_dir = os.getcwd()

    @property
    def actions(self) -> List[str]:
        return ["FILE_READ", "FILE_WRITE"]

    def execute(self, action: str, params: Any, context: Any = None) -> SkillResult:
        # Params expected to be "filename" or {"path": "...", "content": "..."}
        # Simplified: If param is string, it's path. If dict, it has content.
        
        try:
            if action == "FILE_READ":
                path = str(params)
                if not os.path.exists(path):
                    return SkillResult(success=False, message="File not found")
                
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return SkillResult(success=True, message=content[:2000]) # Truncate for memory safety

            elif action == "FILE_WRITE":
                # Need parsing strategy. Planner usually sends JSON string or we handle dicts
                # For this PoC, let's assume params might be a | separated string "path|content" 
                # or the brain handles struct.
                # Let's try to assume params is a string "path|content" for simplicity with current Planner
                if "|" in str(params):
                    path, content = str(params).split("|", 1)
                else:
                    return SkillResult(success=False, message="Format: path|content")
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return SkillResult(success=True, message=f"Wrote to {path}")

            return SkillResult(success=False, message=f"Action {action} not supported")

        except Exception as e:
            return SkillResult(success=False, message=str(e))
