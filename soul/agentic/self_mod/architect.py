"""Architect module - uses LLM to implement creative features and fixes."""

import os
import logging
import json
import re
from pathlib import Path
from typing import Optional, List, Dict
from soul.ollama_client import generate

logger = logging.getLogger(__name__)

class Architect:
    """Uses LLM to architect and implement code changes."""

    def __init__(self, root_path: str):
        self.root = Path(root_path).resolve()

    def implement_task(self, task_description: str) -> Dict:
        """Analyze files and implement the requested task."""
        logger.info(f"🏗️ Architect: Implementing task: {task_description}")
        
        # 1. Context Gathering
        files = self._get_relevant_files()
        context = self._build_context(files)
        
        # 2. Plan & Code Generation
        system_prompt = (
            "You are an S-Tier Senior Software Architect. "
            "Your task is to IMPLEMENT the requested change directly into the codebase. "
            "DO NOT talk. DO NOT explain. DO NOT use 'respond' or 'create_file' JSON. "
            "ONLY output the file paths and their FULL new contents using the specified format."
        )
        
        prompt = f"""
        Task: {task_description}
        
        Project Root: {self.root}
        Files in project: {[f.name for f in files]}
        
        Context (Relevant File Contents):
        {context}
        
        Instruction: 
        Implement the task by providing the FULL content of the files to be updated or created.
        You MUST provide the FULL content, not just the changes.
        
        REQUIRED FORMAT:
        FILE: <path/to/file>
        CONTENT:
        <full file content>
        
        (Repeat for multiple files if needed)
        """
        
        try:
            response = generate(system=system_prompt, prompt=prompt, temperature=0.1, num_predict=4000)
            output = response["response"]
            
            # Save raw for debug
            debug_path = Path("C:/Users/molel/Soul/knowledge/last_architect_output.txt")
            debug_path.write_text(output, encoding="utf-8")
            
            # 3. Apply Changes
            changes = self._apply_output(output)
            
            # AGGRESSIVE EXTRACTION FALLBACK
            if not changes:
                logger.warning("🏗️ Architect: No changes parsed. Attempting Aggressive Extraction...")
                changes = self._aggressive_extraction(output)
            
            return {
                "success": len(changes) > 0,
                "changes_made": len(changes),
                "files": list(changes.keys()),
                "message": f"Implemented: {task_description}" if changes else "No changes applied."
            }
        except Exception as e:
            logger.error(f"🏗️ Architect implementation failed: {e}")
            return {"success": False, "changes_made": 0, "files": [], "message": str(e)}

    def _get_relevant_files(self) -> List[Path]:
        important = ["README.md", "package.json", "requirements.txt", "main.py", "app.py", "index.html", "index.js", "style.css"]
        found = []
        for name in important:
            p = self.root / name
            if p.exists(): found.append(p)
        
        if len(found) < 5:
            for py_p in self.root.rglob("*.py"):
                if py_p not in found and "__pycache__" not in str(py_p): 
                    found.append(py_p)
                    if len(found) >= 10: break
        return found[:10]

    def _build_context(self, files: List[Path]) -> str:
        ctx = ""
        for f in files:
            try:
                rel_path = f.relative_to(self.root)
                content = f.read_text(errors="ignore")[:3000]
                ctx += f"\n--- FILE: {rel_path} ---\n{content}\n"
            except: pass
        return ctx

    def _apply_output(self, output: str) -> Dict[str, str]:
        """Parse output using standard strategies."""
        changes = {}
        
        # Strategy 1: JSON write_file/write_files action (Standard)
        if any(act in output for act in ['"action": "write_file"', '"action": "create_file"', '"action": "write_files"']):
            try:
                json_match = re.search(r"\{.*\}", output, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    params = data.get("parameters", {})
                    # Handle plural 'files' list
                    if "files" in params:
                        for f_data in params["files"]:
                            path = f_data.get("path")
                            content = f_data.get("content")
                            if path and content:
                                changes[path] = self._write_file(path, content)
                    # Handle singular 'path' and 'content'
                    elif "path" in params and "content" in params:
                        path = params["path"]
                        content = params["content"]
                        changes[path] = self._write_file(path, content)
                        
                    if changes: return changes
            except: pass

        # Strategy 2: FILE/CONTENT regex
        pattern = r"(?:FILE:)\s*(.*?)\s*(?:CONTENT:)\s*(.*?)(?=\s*FILE:|$)"
        matches = re.findall(pattern, output, re.DOTALL | re.IGNORECASE)
        for path, content in matches:
            if path and content:
                changes[path.strip()] = self._write_file(path.strip(), content.strip())
        
        return changes

    def _aggressive_extraction(self, output: str) -> Dict[str, str]:
        """Look for code blocks and try to guess their filename if not explicit."""
        changes = {}
        # Look for markdown blocks
        blocks = re.findall(r"```(?:\w+)?\s*(.*?)\s*```", output, re.DOTALL)
        
        if len(blocks) == 1:
            # If only one block and it's a Dockerfile or README, we can guess it
            content = blocks[0]
            if "FROM " in content or "RUN " in content:
                changes["Dockerfile"] = self._write_file("Dockerfile", content)
            elif content.startswith("# "):
                changes["README.md"] = self._write_file("README.md", content)
            elif "import " in content or "def " in content:
                changes["app_update.py"] = self._write_file("app_update.py", content)
        
        # Also check for "answer": "..." in JSON which might contain the code
        if '"answer":' in output:
            try:
                json_match = re.search(r"\{.*\}", output, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    answer = data.get("parameters", {}).get("answer", "")
                    if answer:
                        # Recursively try to apply to the answer string
                        inner_changes = self._apply_output(answer)
                        if not inner_changes:
                            inner_changes = self._aggressive_extraction(answer)
                        changes.update(inner_changes)
            except: pass

        return changes

    def _write_file(self, rel_path: str, content: str) -> str:
        """Helper to write file and return status."""
        try:
            # Clean content if it has markdown backticks
            if content.startswith("```"):
                lines = content.split("\n")
                if lines[0].strip().startswith("```"): lines = lines[1:]
                if lines and lines[-1].strip().startswith("```"): lines = lines[:-1]
                content = "\n".join(lines).strip()
            
            clean_path = rel_path.replace("\\", "/").strip("/").strip("'\"")
            if ":" in clean_path: clean_path = clean_path.split(":")[-1].strip("/")
            
            target = self.root / clean_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            logger.info(f"📝 Architect: Updated {clean_path}")
            return "updated"
        except Exception as e:
            logger.error(f"Failed to write {rel_path}: {e}")
            return "failed"
