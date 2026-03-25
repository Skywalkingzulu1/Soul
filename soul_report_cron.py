import time
import os
import sys
import logging
import json
from datetime import datetime

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from soul.memory import Memory

def generate_report():
    memory = Memory()
    
    # 1. Fetch latest goal
    goals = memory.recall("goal_setting", n=1, memory_type="goal_setting")
    latest_goal = goals[0] if goals else "No active goal found."
    
    # 2. Fetch latest actions
    actions = memory.recall("goal_directed_learning", n=5, memory_type="goal_directed_learning")
    
    # 3. Fetch latest observations
    observations = memory.recall("observation", n=3, memory_type="observation")
    
    # 4. Format Report
    report = f"""
============================================================
  ANDILE SOUL - AUTONOMOUS STATUS REPORT
  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
============================================================

LATEST GOAL:
{latest_goal}

RECENT ACTIONS TOWARD GOAL:
"""
    for a in actions:
        report += f"- {a}\n"
        
    report += "\nVISUAL OBSERVATIONS:\n"
    for o in observations:
        report += f"- {o[:100]}...\n"
        
    report += "\n============================================================\n"
    
    # Append to log file
    log_path = "knowledge/autonomous_reports.log"
    with open(log_path, "a") as f:
        f.write(report)
        
    # Print to console for current session visibility
    print(report)

if __name__ == "__main__":
    while True:
        try:
            generate_report()
        except Exception as e:
            print(f"Report generation failed: {e}")
        
        # Sleep for 20 minutes
        print("\nNext report in 20 minutes... (Zzz)")
        time.sleep(20 * 60)
