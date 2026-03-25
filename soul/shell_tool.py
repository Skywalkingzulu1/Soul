import subprocess
import os
import logging

logger = logging.getLogger(__name__)

class ShellTool:
    """Advanced shell interaction tool for the Super Agent."""
    
    def __init__(self, workspace_dir=None) -> None:
        self.workspace_dir = workspace_dir or os.getcwd()
        
    def execute(self, command, timeout=30) -> None:
        """Execute a shell command with safety boundaries."""
        # Safety filter (basic)
        forbidden = ["rm -rf /", "del /f /s /q C:\\", "mkfs"]
        if any(f in command for f in forbidden):
            return "Error: Command blocked by security guardrails."
            
        try:
            logger.info(f"Executing shell: {command}")
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=self.workspace_dir, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            
            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout[:2000]}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr[:2000]}\n"
                
            if not output:
                output = f"Command executed successfully (Exit code: {result.returncode}) with no output."
                
            return output
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds."
        except Exception as e:
            return f"Error executing shell command: {str(e)}"
