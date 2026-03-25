"""100 safe computer actions test for Andile Sizophila.

Tests: vision, keyboard, mouse, file operations, system queries,
math, text processing, and web interactions.

All actions are SAFE — no destructive operations, no network calls
that could harm anything.
"""

import asyncio
import sys
import os
import time
import logging

sys.path.insert(0, os.path.dirname(__file__))
logging.basicConfig(level=logging.WARNING)

passed = 0
failed = 0
results = []


def record(num, action, success, detail=""):
    global passed, failed
    if success:
        passed += 1
        status = "PASS"
    else:
        failed += 1
        status = "FAIL"
    results.append({"num": num, "action": action, "status": status, "detail": detail})
    print(f"  [{num:3}/100] {status}: {action}")
    if detail and status == "FAIL":
        print(f"           -> {detail}")


async def main():
    print("=" * 60)
    print("  ANDILE SIZOPHILA - 100 SAFE ACTIONS TEST")
    print("=" * 60)

    # Start ollama first
    from server import start_ollama

    print("\nStarting ollama...")
    start_ollama()

    # === GROUP 1: VISION (10 actions) ===
    print("\n--- VISION (1-10) ---")
    from soul.vision.eyes import Eyes

    eyes = Eyes()

    # 1. Initialize vision
    try:
        state = eyes.get_state()
        record(1, "Initialize vision system", state.get("initialized", False))
    except Exception as e:
        record(1, "Initialize vision system", False, str(e))

    # 2. Capture screen
    try:
        vision = eyes.see()
        record(
            2,
            "Capture screen",
            vision.get("screen_size") is not None,
            f"Size: {vision.get('screen_size')}",
        )
    except Exception as e:
        record(2, "Capture screen", False, str(e))

    # 3. Read screen text
    try:
        text = vision.get("text", "")
        record(3, "Read screen text (OCR)", len(text) > 0, f"Chars: {len(text)}")
    except Exception as e:
        record(3, "Read screen text (OCR)", False, str(e))

    # 4. Get screen summary
    try:
        summary = vision.get("summary", "")
        record(4, "Get screen summary", len(summary) > 0, f"Length: {len(summary)}")
    except Exception as e:
        record(4, "Get screen summary", False, str(e))

    # 5. Get text boxes
    try:
        boxes = vision.get("text_boxes", [])
        record(5, "Get text bounding boxes", len(boxes) > 0, f"Boxes: {len(boxes)}")
    except Exception as e:
        record(5, "Get text bounding boxes", False, str(e))

    # 6. Save screenshot
    try:
        path = eyes.save_screenshot("screenshots/test_action6.png")
        record(6, "Save screenshot", path is not None and os.path.exists(path))
    except Exception as e:
        record(6, "Save screenshot", False, str(e))

    # 7. Find text on screen
    try:
        matches = eyes.find("test")
        record(7, "Search for text on screen", True, f"Matches: {len(matches)}")
    except Exception as e:
        record(7, "Search for text on screen", False, str(e))

    # 8. Get vision state
    try:
        state = eyes.get_state()
        record(8, "Get vision state", "initialized" in state)
    except Exception as e:
        record(8, "Get vision state", False, str(e))

    # 9. Second capture (test persistence)
    try:
        vision2 = eyes.see()
        record(9, "Second screen capture", vision2.get("screen_size") is not None)
    except Exception as e:
        record(9, "Second screen capture", False, str(e))

    # 10. Vision log count
    try:
        record(
            10,
            "Vision log tracking",
            len(eyes.vision_log) >= 2,
            f"Entries: {len(eyes.vision_log)}",
        )
    except Exception as e:
        record(10, "Vision log tracking", False, str(e))

    # === GROUP 2: AGENTIC (10 actions) ===
    print("\n--- AGENTIC (11-20) ---")

    from soul.agentic.perceive import analyze_screen, decide_action

    # 11. Analyze screen
    try:
        analysis = analyze_screen(text[:500], "User is working on code")
        record(
            11, "Analyze screen content", len(analysis) > 10, f"Length: {len(analysis)}"
        )
    except Exception as e:
        record(11, "Analyze screen content", False, str(e))

    # 12. Decide action
    try:
        action = decide_action(text[:300], analysis, "check the time")
        record(
            12, "Decide action", "action" in action, f"Action: {action.get('action')}"
        )
    except Exception as e:
        record(12, "Decide action", False, str(e))

    # 13. Action executor init
    from soul.agentic.act import ActionExecutor

    executor = ActionExecutor()
    try:
        executor._init()
        record(13, "Initialize action executor", executor._pyautogui is not None)
    except Exception as e:
        record(13, "Initialize action executor", False, str(e))

    # 14. Get mouse position
    try:
        pos = executor.get_mouse_position()
        record(14, "Get mouse position", pos is not None, f"Position: {pos}")
    except Exception as e:
        record(14, "Get mouse position", False, str(e))

    # 15. Move mouse (safe — moves to center)
    try:
        ok = executor.move(960, 600, duration=0.1)
        record(15, "Move mouse to center", ok)
    except Exception as e:
        record(15, "Move mouse to center", False, str(e))

    # 16. Press a key (safe — Escape)
    try:
        ok = executor.press("escape")
        record(16, "Press Escape key", ok)
    except Exception as e:
        record(16, "Press Escape key", False, str(e))

    # 17. Press a letter key
    try:
        ok = executor.press("a")
        record(17, "Press letter key", ok)
    except Exception as e:
        record(17, "Press letter key", False, str(e))

    # 18. Get executor state
    try:
        state = executor.get_state()
        record(
            18, "Get executor state", "actions" in state, f"Actions: {state['actions']}"
        )
    except Exception as e:
        record(18, "Get executor state", False, str(e))

    # 19. Agentic loop init
    from soul.agentic.loop import AgenticLoop
    from soul.brain import Soul
    from server import start_ollama

    start_ollama()
    soul = Soul(name="Andile Sizophila Mchunu")
    loop = AgenticLoop(soul)
    try:
        state = loop.get_state()
        record(19, "Initialize agentic loop", not state["running"])
    except Exception as e:
        record(19, "Initialize agentic loop", False, str(e))

    # 20. Agentic loop state
    try:
        record(20, "Agentic loop has goal tracking", "goal" in state)
    except Exception as e:
        record(20, "Agentic loop has goal tracking", False, str(e))

    # === GROUP 3: PHILOSOPHY (10 actions) ===
    print("\n--- PHILOSOPHY (21-30) ---")

    from soul.philosophy.knowledge import search_philosophy, get_philosophy_knowledge
    from soul.philosophy.consciousness import ConsciousnessTracker
    from soul.philosophy.dialectic import DialecticEngine

    # 21. Load philosophy knowledge
    try:
        concepts = get_philosophy_knowledge()
        record(
            21,
            "Load philosophy concepts",
            len(concepts) > 100,
            f"Count: {len(concepts)}",
        )
    except Exception as e:
        record(21, "Load philosophy concepts", False, str(e))

    # 22. Search philosophy
    try:
        results = search_philosophy("I think therefore I am", n=3)
        record(22, "Search philosophy", len(results) > 0, f"Results: {len(results)}")
    except Exception as e:
        record(22, "Search philosophy", False, str(e))

    # 23. Consciousness tracker
    try:
        ct = ConsciousnessTracker(soul.memory)
        ct.log_thought("test", "Testing consciousness")
        state = ct.get_state()
        record(23, "Consciousness tracking", state["thoughts_processed"] > 0)
    except Exception as e:
        record(23, "Consciousness tracking", False, str(e))

    # 24. Doubt (Descartes)
    try:
        result = ct.doubt("Am I conscious?")
        record(24, "Descartes doubt", result["doubted"])
    except Exception as e:
        record(24, "Descartes doubt", False, str(e))

    # 25. Rationalist view
    try:
        view = ct.rationalist_view()
        record(25, "Rationalist view", "computation" in view.lower())
    except Exception as e:
        record(25, "Rationalist view", False, str(e))

    # 26. Empiricist view
    try:
        view = ct.empiricist_view()
        record(26, "Empiricist view", "sensory" in view.lower())
    except Exception as e:
        record(26, "Empiricist view", False, str(e))

    # 27. Synthesis
    try:
        view = ct.synthesis()
        record(27, "Consciousness synthesis", "i process" in view.lower())
    except Exception as e:
        record(27, "Consciousness synthesis", False, str(e))

    # 28. Dialectic engine
    try:
        de = DialecticEngine(search_philosophy)
        result = de.full_dialectic("AI can be conscious")
        record(28, "Dialectic (thesis-antithesis-synthesis)", "synthesis" in result)
    except Exception as e:
        record(28, "Dialectic (thesis-antithesis-synthesis)", False, str(e))

    # 29. Socratic questions
    try:
        questions = de.socratic_question("Machines can think")
        record(
            29,
            "Generate Socratic questions",
            len(questions) > 5,
            f"Questions: {len(questions)}",
        )
    except Exception as e:
        record(29, "Generate Socratic questions", False, str(e))

    # 30. SA identity
    try:
        from soul.philosophy.sa_identity import get_sa_context

        ctx = get_sa_context()
        record(30, "Load SA identity", "ubuntu" in ctx.lower())
    except Exception as e:
        record(30, "Load SA identity", False, str(e))

    # === GROUP 4: BRAIN MODULES (10 actions) ===
    print("\n--- BRAIN (31-40) ---")

    # 31. Load brain modules (trigger lazy loading first)
    try:
        soul.brain.process({"text": "hello"})
        stats = soul.brain.get_stats()
        record(
            31,
            "Load brain modules",
            stats["total_modules"] > 0,
            f"Modules: {stats['total_modules']}",
        )
    except Exception as e:
        record(31, "Load brain modules", False, str(e))

    # 32. Process through brain
    try:
        result = soul.brain.process({"text": "Hello world"})
        record(
            32,
            "Process through brain",
            "categories" in result,
            f"Categories: {result['categories']}",
        )
    except Exception as e:
        record(32, "Process through brain", False, str(e))

    # 33. Thalamic gateway routing
    from soul.orchestrator import ThalamicGateway

    gw = ThalamicGateway()
    try:
        cats = gw.route("I feel happy")
        record(
            33, "Thalamic gateway (emotion)", "emotion" in cats, f"Routed to: {cats}"
        )
    except Exception as e:
        record(33, "Thalamic gateway (emotion)", False, str(e))

    # 34. Gateway: question
    try:
        cats = gw.route("What is Python?")
        record(34, "Thalamic gateway (question)", "executive" in cats)
    except Exception as e:
        record(34, "Thalamic gateway (question)", False, str(e))

    # 35. Gateway: action
    try:
        cats = gw.route("Send an email to test@example.com")
        record(35, "Thalamic gateway (action)", "executive" in cats or "habit" in cats)
    except Exception as e:
        record(35, "Thalamic gateway (action)", False, str(e))

    # 36. Gateway: memory
    try:
        cats = gw.route("Remember what I told you yesterday")
        record(36, "Thalamic gateway (memory)", "memory" in cats)
    except Exception as e:
        record(36, "Thalamic gateway (memory)", False, str(e))

    # 37. Global workspace
    from soul.orchestrator import GlobalWorkspace

    ws = GlobalWorkspace()
    try:
        winners = ws.compete(
            [{"confidence": 0.8, "area": "test"}, {"confidence": 0.5, "area": "test2"}]
        )
        record(
            37,
            "Global workspace competition",
            len(winners) > 0,
            f"Winners: {len(winners)}",
        )
    except Exception as e:
        record(37, "Global workspace competition", False, str(e))

    # 38. Workspace broadcast
    try:
        broadcast = ws.broadcast(winners)
        record(38, "Global workspace broadcast", "summary" in broadcast)
    except Exception as e:
        record(38, "Global workspace broadcast", False, str(e))

    # 39. Thinker engine
    try:
        from soul.thinker import ThinkerEngine

        t = ThinkerEngine(name="Test")
        result = t.direct("What is 2+2?", identity="Test", conversation="")
        record(
            39,
            "Thinker direct answer",
            "4" in result or "four" in result.lower(),
            f"Answer: {result[:50]}",
        )
    except Exception as e:
        record(39, "Thinker direct answer", False, str(e))

    # 40. Thinker complexity
    try:
        comp = t.assess_complexity("What is 2+2?")
        record(
            40,
            "Thinker complexity assessment",
            comp in ["simple", "complex", "debate", "explore"],
            f"Level: {comp}",
        )
    except Exception as e:
        record(40, "Thinker complexity assessment", False, str(e))

    # === GROUP 5: MEMORY (10 actions) ===
    print("\n--- MEMORY (41-50) ---")

    # 41. Store memory
    try:
        mid = soul.memory.store("test", "Testing memory system", importance=0.5)
        record(41, "Store memory", mid is not None)
    except Exception as e:
        record(41, "Store memory", False, str(e))

    # 42. Recall memory
    try:
        results = soul.memory.recall("testing memory", n=3)
        record(42, "Recall memory", len(results) > 0, f"Results: {len(results)}")
    except Exception as e:
        record(42, "Recall memory", False, str(e))

    # 43. Store conversation
    try:
        soul.memory.store_conversation("user", "test message")
        record(43, "Store conversation", True)
    except Exception as e:
        record(43, "Store conversation", False, str(e))

    # 44. Get conversation
    try:
        conv = soul.memory.get_recent_conversation(n=5)
        record(44, "Get conversation history", len(conv) > 0, f"Entries: {len(conv)}")
    except Exception as e:
        record(44, "Get conversation history", False, str(e))

    # 45. Memory count
    try:
        count = soul.memory.count()
        record(45, "Memory count", count > 0, f"Count: {count}")
    except Exception as e:
        record(45, "Memory count", False, str(e))

    # 46. Identity get/set
    try:
        soul.memory.set_identity("test_key", "test_value")
        val = soul.memory.get_identity("test_key")
        record(46, "Identity get/set", val == "test_value")
    except Exception as e:
        record(46, "Identity get/set", False, str(e))

    # 47. Planner
    try:
        plan = soul.planner.plan("What is 2+2?")
        record(
            47,
            "Planner plan generation",
            "approach" in plan,
            f"Approach: {plan['approach']}",
        )
    except Exception as e:
        record(47, "Planner plan generation", False, str(e))

    # 48. Planner: signup signal
    try:
        plan = soul.planner.plan("Sign up for GitHub")
        record(
            48,
            "Planner signup detection",
            plan["approach"] == "signup",
            f"Approach: {plan['approach']}",
        )
    except Exception as e:
        record(48, "Planner signup detection", False, str(e))

    # 49. Planner: email signal
    try:
        plan = soul.planner.plan("Send email to test@example.com saying hello")
        record(
            49,
            "Planner email detection",
            plan["approach"] == "email",
            f"Approach: {plan['approach']}",
        )
    except Exception as e:
        record(49, "Planner email detection", False, str(e))

    # 50. Memory persistence
    try:
        soul.memory.store("persist_test", "This should persist", importance=0.8)
        results = soul.memory.recall("persist", n=1)
        record(50, "Memory persistence", len(results) > 0)
    except Exception as e:
        record(50, "Memory persistence", False, str(e))

    # === GROUP 6: IDENTITY & CLOCK (10 actions) ===
    print("\n--- IDENTITY & CLOCK (51-60) ---")

    # 51. Identity name
    try:
        record(
            51,
            "Identity name",
            "Andile" in soul.identity.name,
            f"Name: {soul.identity.name}",
        )
    except Exception as e:
        record(51, "Identity name", False, str(e))

    # 52. Identity traits
    try:
        record(
            52,
            "Identity traits",
            "direct" in soul.identity.traits,
            f"Traits: {soul.identity.traits[:50]}",
        )
    except Exception as e:
        record(52, "Identity traits", False, str(e))

    # 53. Identity self model
    try:
        model = soul.identity.get_self_model()
        record(53, "Identity self model", "Andile" in model, f"Length: {len(model)}")
    except Exception as e:
        record(53, "Identity self model", False, str(e))

    # 54. Twin system prompt
    try:
        prompt = soul.identity.get_twin_system_prompt()
        record(54, "Twin system prompt", "Andile" in prompt, f"Length: {len(prompt)}")
    except Exception as e:
        record(54, "Twin system prompt", False, str(e))

    # 55. Clock current time
    try:
        now = soul.clock.now()
        record(
            55,
            "Clock current time",
            now is not None,
            f"Time: {now.strftime('%H:%M:%S')}",
        )
    except Exception as e:
        record(55, "Clock current time", False, str(e))

    # 56. Clock time of day
    try:
        tod = soul.clock.time_of_day()
        record(
            56,
            "Clock time of day",
            tod in ["morning", "afternoon", "evening", "night"],
            f"Time: {tod}",
        )
    except Exception as e:
        record(56, "Clock time of day", False, str(e))

    # 57. Clock session duration
    try:
        dur = soul.clock.session_duration()
        record(57, "Clock session duration", len(dur) > 0, f"Duration: {dur}")
    except Exception as e:
        record(57, "Clock session duration", False, str(e))

    # 58. System info
    try:
        info = soul.system.summary()
        record(58, "System info", "CPU" in info, f"Info: {info}")
    except Exception as e:
        record(58, "System info", False, str(e))

    # 59. System capabilities
    try:
        caps = soul.system.capabilities
        record(59, "System capabilities", len(caps) > 5, f"Capabilities: {len(caps)}")
    except Exception as e:
        record(59, "System capabilities", False, str(e))

    # 60. System limitations
    try:
        lims = soul.system.limitations
        record(60, "System limitations", len(lims) > 3, f"Limitations: {len(lims)}")
    except Exception as e:
        record(60, "System limitations", False, str(e))

    # === GROUP 7: TOOLS (10 actions) ===
    print("\n--- TOOLS (61-70) ---")

    # 61. Tool registry
    try:
        tools = soul.tools.tools
        record(61, "Tool registry", len(tools) > 0, f"Tools: {list(tools.keys())}")
    except Exception as e:
        record(61, "Tool registry", False, str(e))

    # 62. Tool description
    try:
        desc = ""
        for name, tool in soul.tools.tools.items():
            if tool and hasattr(tool, "description"):
                desc += f"{name}: {tool.description}\n"
        record(
            62, "Tool descriptions", len(desc) > 10, f"Tools: {len(soul.tools.tools)}"
        )
    except Exception as e:
        record(62, "Tool descriptions", False, str(e))

    # 63. Code execution
    try:
        result = await soul.tools.execute("code", "print('hello from Andile')")
        record(
            63, "Code execution", "hello" in result.lower(), f"Output: {result[:50]}"
        )
    except Exception as e:
        record(63, "Code execution", False, str(e))

    # 64. Code: math
    try:
        result = await soul.tools.execute("code", "print(2 + 2)")
        record(64, "Code: math", "4" in result)
    except Exception as e:
        record(64, "Code: math", False, str(e))

    # 65. Code: list comprehension
    try:
        result = await soul.tools.execute("code", "print([x**2 for x in range(5)])")
        record(65, "Code: list comprehension", "[0" in result)
    except Exception as e:
        record(65, "Code: list comprehension", False, str(e))

    # 66. Code: string manipulation
    try:
        result = await soul.tools.execute("code", "print('hello'.upper())")
        record(66, "Code: string manipulation", "HELLO" in result)
    except Exception as e:
        record(66, "Code: string manipulation", False, str(e))

    # 67. Code: file operations
    try:
        result = await soul.tools.execute("code", "import os; print(os.getcwd())")
        record(67, "Code: file operations", "Soul" in result or "molel" in result)
    except Exception as e:
        record(67, "Code: file operations", False, str(e))

    # 68. Code: json
    try:
        result = await soul.tools.execute(
            "code", "import json; print(json.dumps({'test': True}))"
        )
        record(68, "Code: JSON", "test" in result)
    except Exception as e:
        record(68, "Code: JSON", False, str(e))

    # 69. Code: datetime
    try:
        result = await soul.tools.execute(
            "code",
            "import datetime; print(datetime.datetime.now().strftime('%Y-%m-%d'))",
        )
        record(69, "Code: datetime", "2026" in result)
    except Exception as e:
        record(69, "Code: datetime", False, str(e))

    # 70. Web search
    try:
        result = await soul.tools.execute("search", "Python programming language")
        record(70, "Web search", len(result) > 50, f"Result: {result[:80]}")
    except Exception as e:
        record(70, "Web search", False, str(e))

    # === GROUP 8: SOUL PERCEIVE (5 LLM actions) ===
    print("\n--- SOUL PERCEIVE (71-75) ---")

    # 71. Simple question
    try:
        r = await soul.perceive("What is 2+2?")
        record(
            71, "Simple question", "4" in r or "four" in r.lower(), f"Answer: {r[:50]}"
        )
    except Exception as e:
        record(71, "Simple question", False, str(e))

    # 72. Identity question
    try:
        r = await soul.perceive("Who are you?")
        record(
            72,
            "Identity question",
            "andile" in r.lower() or "sizophila" in r.lower(),
            f"Answer: {r[:60]}",
        )
    except Exception as e:
        record(72, "Identity question", False, str(e))

    # 73. System question
    try:
        r = await soul.perceive("What can you do?")
        record(73, "System question", len(r) > 20, f"Answer: {r[:60]}")
    except Exception as e:
        record(73, "System question", False, str(e))

    # 74. Command: /status
    try:
        status = soul.status()
        record(74, "/status command", "Andile" in status, f"Status: {status[:60]}")
    except Exception as e:
        record(74, "/status command", False, str(e))

    # 75. Brain modules after perceive
    try:
        stats = soul.brain.get_stats()
        record(
            75,
            "Brain modules active after perceive",
            stats["active_modules"] > 0,
            f"Active: {stats['active_modules']}",
        )
    except Exception as e:
        record(75, "Brain modules active after perceive", False, str(e))

    # 76. Memory after perceive
    try:
        count = soul.memory.count()
        record(76, "Memory count after perceive", count > 10, f"Count: {count}")
    except Exception as e:
        record(76, "Memory count after perceive", False, str(e))

    # 77. Interaction count
    try:
        record(
            77,
            "Interaction count",
            soul.interaction_count >= 3,
            f"Count: {soul.interaction_count}",
        )
    except Exception as e:
        record(77, "Interaction count", False, str(e))

    # 78. Consciousness tracker
    try:
        ct_state = soul.consciousness.get_state()
        record(78, "Consciousness state", ct_state["thoughts_processed"] >= 0)
    except Exception as e:
        record(78, "Consciousness state", False, str(e))

    # 79. Dialectic engine
    try:
        result = soul.dialectic.full_dialectic("Machines can think")
        record(79, "Dialectic engine", "synthesis" in result)
    except Exception as e:
        record(79, "Dialectic engine", False, str(e))

    # 80. Full status
    try:
        status = soul.status()
        record(80, "Full status report", "Brain:" in status and "Philosophy:" in status)
    except Exception as e:
        record(80, "Full status report", False, str(e))

    # === GROUP 9: ADVANCED (10 actions) ===
    print("\n--- ADVANCED (81-90) ---")

    # 81. Chain of thought
    try:
        r = soul.thinker.chain_of_thought(
            "Why is the sky blue?", context="Physics question"
        )
        record(81, "Chain of thought", len(r) > 20, f"Length: {len(r)}")
    except Exception as e:
        record(81, "Chain of thought", False, str(e))

    # 82. Debate system
    try:
        r = soul.debate.run("Should AI have rights?", rounds=1)
        record(82, "Debate system", len(r) > 20, f"Length: {len(r)}")
    except Exception as e:
        record(82, "Debate system", False, str(e))

    # 83. Reflection
    try:
        r = soul.reflector.reflect("What is 2+2?", "4")
        record(
            83,
            "Reflection",
            r is not None and len(r) > 10,
            f"Length: {len(r) if r else 0}",
        )
    except Exception as e:
        record(83, "Reflection", False, str(e))

    # 84. Planner decomposition
    try:
        steps = soul.planner.decompose("Build a web scraper for DeFi protocols")
        record(84, "Task decomposition", len(steps) > 0, f"Steps: {len(steps)}")
    except Exception as e:
        record(84, "Task decomposition", False, str(e))

    # 85. SA identity context
    try:
        from soul.philosophy.sa_identity import get_sa_context

        ctx = get_sa_context()
        record(85, "SA identity context", "Constitution" in ctx)
    except Exception as e:
        record(85, "SA identity context", False, str(e))

    # 86. Value statement
    try:
        from soul.philosophy.weights import get_value_statement

        stmt = get_value_statement()
        record(86, "Value statement", "Ubuntu" in stmt)
    except Exception as e:
        record(86, "Value statement", False, str(e))

    # 87. Philosophy search: Ubuntu
    try:
        results = search_philosophy("Ubuntu I am because we are", n=3)
        record(87, "Philosophy search: Ubuntu", len(results) > 0)
    except Exception as e:
        record(87, "Philosophy search: Ubuntu", False, str(e))

    # 88. Philosophy search: Democracy
    try:
        results = search_philosophy("democracy and human rights", n=3)
        record(88, "Philosophy search: Democracy", len(results) > 0)
    except Exception as e:
        record(88, "Philosophy search: Democracy", False, str(e))

    # 89. Consciousness rationalist
    try:
        view = soul.consciousness.rationalist_view()
        record(89, "Consciousness: Rationalist", "computation" in view.lower())
    except Exception as e:
        record(89, "Consciousness: Rationalist", False, str(e))

    # 90. Consciousness synthesis
    try:
        view = soul.consciousness.synthesis()
        record(90, "Consciousness: Synthesis", "i process" in view.lower())
    except Exception as e:
        record(90, "Consciousness: Synthesis", False, str(e))

    # === GROUP 10: INTEGRATION (10 actions) ===
    print("\n--- INTEGRATION (91-100) ---")

    # 91. Vision + brain integration
    try:
        vision = eyes.see()
        brain_result = soul.brain.process({"text": vision.get("text", "")[:200]})
        record(91, "Vision + Brain integration", "categories" in brain_result)
    except Exception as e:
        record(91, "Vision + Brain integration", False, str(e))

    # 92. Philosophy + memory integration
    try:
        soul.memory.store("philosophy", "Ubuntu: I am because we are", importance=0.9)
        results = soul.memory.recall("Ubuntu", n=1)
        record(92, "Philosophy + Memory integration", len(results) > 0)
    except Exception as e:
        record(92, "Philosophy + Memory integration", False, str(e))

    # 93. Clock + identity integration
    try:
        now = soul.clock.now()
        identity = soul.identity.name
        record(93, "Clock + Identity", now is not None and "Andile" in identity)
    except Exception as e:
        record(93, "Clock + Identity", False, str(e))

    # 94. System + tools integration
    try:
        caps = soul.system.capabilities
        tools = soul.tools.tools
        record(94, "System + Tools", len(caps) > 0 and len(tools) > 0)
    except Exception as e:
        record(94, "System + Tools", False, str(e))

    # 95. Planner + thinker integration
    try:
        plan = soul.planner.plan("How does recursion work?")
        if plan["approach"] == "direct":
            r = soul.thinker.direct("How does recursion work?")
        else:
            r = soul.thinker.chain_of_thought("How does recursion work?")
        record(95, "Planner + Thinker integration", len(r) > 20)
    except Exception as e:
        record(95, "Planner + Thinker integration", False, str(e))

    # 96. Full perceive pipeline
    try:
        r = await soul.perceive("Explain what a computer is")
        record(96, "Full perceive pipeline", len(r) > 20, f"Length: {len(r)}")
    except Exception as e:
        record(96, "Full perceive pipeline", False, str(e))

    # 97. Memory recall after multiple interactions
    try:
        recall_results = soul.memory.recall("computer", n=3)
        record(
            97,
            "Memory recall (cross-interaction)",
            True,
            f"Results: {len(recall_results)}",
        )
    except Exception as e:
        record(97, "Memory recall (cross-interaction)", False, str(e))

    # 98. Interaction count final
    try:
        record(
            98,
            "Interaction count final",
            soul.interaction_count >= 10,
            f"Count: {soul.interaction_count}",
        )
    except Exception as e:
        record(98, "Interaction count final", False, str(e))

    # 99. Full status final
    try:
        status = soul.status()
        record(99, "Final status", len(status) > 100)
    except Exception as e:
        record(99, "Final status", False, str(e))

    # 100. Soul alive
    try:
        record(
            100,
            "Soul alive and processing",
            soul.interaction_count > 0 and soul.memory.count() > 0,
        )
    except Exception as e:
        record(100, "Soul alive and processing", False, str(e))

    # === FINAL REPORT ===
    print(f"\n{'=' * 60}")
    print(f"  FINAL REPORT")
    print(f"{'=' * 60}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Total:  {passed + failed}")
    print(f"  Rate:   {passed / (passed + failed) * 100:.1f}%")
    print(f"{'=' * 60}")

    if failed > 0:
        print(f"\n  FAILED ACTIONS:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"    #{r['num']}: {r['action']} -> {r['detail']}")

    grade = (
        "A+"
        if passed >= 95
        else "A"
        if passed >= 90
        else "B"
        if passed >= 80
        else "C"
        if passed >= 70
        else "D"
        if passed >= 60
        else "F"
    )
    print(f"\n  Grade: {grade} ({passed}/100)")


if __name__ == "__main__":
    asyncio.run(main())
