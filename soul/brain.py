import logging
import time
import asyncio
import os
import ollama

from soul.memory import Memory
from soul.identity import Identity
from soul.thinker import ThinkerEngine
from soul.debate import DebateSystem
from soul.reflection import Reflector
from soul.tools import ToolRegistry
from soul.planner import Planner
from soul.clock import Clock
from soul.system_info import SystemInfo
from soul.orchestrator import BrainOrchestrator
from soul.state import state_machine
from soul.philosophy.consciousness import ConsciousnessTracker
from soul.philosophy.dialectic import DialecticEngine
from soul.philosophy.knowledge import search_philosophy, get_philosophy_knowledge
from soul.philosophy.sa_identity import get_sa_context
from soul.philosophy.weights import get_value_statement

try:
    from soul.agentic.self_mod import AgenticExecutor

    AGENTIC_AVAILABLE = True
except ImportError:
    AGENTIC_AVAILABLE = False

logger = logging.getLogger(__name__)


class Soul:
    """Digital twin of Andile Sizophila Mchunu.

    Plan-then-execute architecture:
    1. PLANNER decides approach (direct/think/debate/search/decompose/code)
    2. EXECUTOR carries out the plan
    3. SYNTHESIZER combines results for complex tasks

    Self-aware of time, system limitations, and available tools.
    """

    def __init__(self, name=None):
        self.memory = Memory()
        self.identity = Identity(self.memory)
        self.clock = Clock()
        self.system = SystemInfo()

        if name:
            self.identity.name = name
            self.memory.set_identity("name", name)

        self.thinker = ThinkerEngine(name=self.identity.name)
        self.debate = DebateSystem()
        self.reflector = Reflector(self.memory)
        self.tools = ToolRegistry()
        self.planner = Planner(thinker=self.thinker)
        self.brain = BrainOrchestrator()  # All 216 modules
        self.consciousness = ConsciousnessTracker(self.memory)  # Track thinking
        self.dialectic = DialecticEngine(search_philosophy)  # Philosophical debate

        self._browser_loaded = False
        self.interaction_count = 0

        if AGENTIC_AVAILABLE:
            try:
                self.agentic = AgenticExecutor()
                logger.info("Agentic self-modification enabled")
            except Exception as e:
                logger.warning(f"Agentic executor unavailable: {e}")
                self.agentic = None
        else:
            self.agentic = None

        # Store SA identity and values in memory
        self.memory.store(
            "identity", get_sa_context(), importance=1.0, confidence="verified"
        )
        self.memory.store(
            "values", get_value_statement(), importance=1.0, confidence="verified"
        )

    def _load_browser(self):
        if not self._browser_loaded:
            try:
                from browser.web_agent import BrowserTool

                self.tools.register("browser", BrowserTool())
                logger.info("Browser tool loaded.")
            except ImportError:
                logger.warning("browser-use not available. Browser tool disabled.")
            self._browser_loaded = True

    def _get_context(self, question):
        # Prioritize recent actions if asking about activity
        q_lower = question.lower()
        if any(
            w in q_lower for w in ["doing", "done", "what did you", "tasks", "today"]
        ):
            actions = self.memory.recall(
                "recent actions activities", n=10, memory_type="action"
            )
            if actions:
                return "RECENT ACTIONS:\n" + "\n".join(f"- {a}" for a in actions)

        memories = self.memory.recall(question, n=5)
        if memories:
            return "RELEVANT MEMORIES:\n" + "\n".join(f"- {m}" for m in memories)
        return "No prior context."

    def _get_conversation_context(self, n=3):
        history = self.memory.get_recent_conversation(n=n)
        if not history:
            return ""
        lines = []
        for msg in history[-10:]:  # Last 10 messages
            role = "You" if msg["role"] == "user" else "Me"
            # Increased truncation to preserve more context
            content = msg["content"][:300]
            lines.append(f"{role}: {content}")
        return "\n".join(lines)

    def _is_personal_question(self, text):
        personal_signals = [
            "who are you",
            "what is your name",
            "tell me about yourself",
            "what do you do",
            "your background",
            "what have you done",
            "what did you do",
            "what are you doing",
            "been doing",
            "your tasks",
            "today",
            "your projects",
            "your trading",
            "andile",
            "skywalkingzulu",
            "azania",
            "your strategy",
            "your system",
            "your limitations",
            "what can you do",
            "your capabilities",
            "your tools",
            "are you in a relationship",
            "are you engaged",
            "are you married",
            "do you have a",
            "who are you",
            "what is your name",
            "tell me about yourself",
            "what do you do for",
            "where do you live",
            "your location",
            "your moniker",
        ]
        text_lower = text.lower()
        return any(sig in text_lower for sig in personal_signals)

    async def perceive(self, input_text, source="user"):
        self.interaction_count += 1
        start_time = time.time()

        self.memory.store_conversation("user", input_text)
        self.memory.store(
            "observation", f"User said: {input_text}", importance=0.4, confidence="user"
        )

        # Process through all 216 brain modules
        brain_output = self.brain.process({"text": input_text})
        self.memory.store(
            "brain_activation",
            f"Modules: {brain_output['modules_active']} active, "
            f"Categories: {brain_output['categories']}",
            importance=0.3,
        )

        # Handle commands
        if input_text.startswith("/tool "):
            return await self._handle_tool_command(input_text[6:])

        if input_text.lower().startswith("/agent "):
            return self._handle_agentic_command(input_text[7:].strip())

        if input_text.lower().startswith("confirm "):
            cmd = input_text[8:].strip()
            state_machine.update(
                state="EXECUTING",
                action=f"Forced Shell Command: {cmd[:20]}",
                tool="shell",
            )
            shell_result = await self.tools.execute("shell", cmd)
            self.memory.store(
                "action",
                f"Executed explicitly confirmed shell command: {cmd}. Result: {shell_result[:200]}...",
                importance=0.9,
            )
            state_machine.update(state="IDLE", clear_tool=True)
            return f"Forced Execution Complete:\n{shell_result}"

        # Plan Mode - show what would happen without executing
        if input_text.lower().startswith("/plan "):
            question = input_text[6:].strip()
            plan = self.planner.plan(question)
            approach = plan.get("approach", "unknown")
            reason = plan.get("reason", "No reason")
            steps = plan.get("steps", [])
            needs_search = plan.get("needs_search", False)

            plan_desc = f"PLAN FOR: {question}\n\n"
            plan_desc += f"Approach: {approach}\n"
            plan_desc += f"Reason: {reason}\n"
            plan_desc += f"Needs Search: {needs_search}\n"

            if steps:
                plan_desc += f"\nSteps:\n"
                for i, step in enumerate(steps, 1):
                    plan_desc += f"  {i}. {step}\n"

            # Check what tools would be used
            if approach in (
                "shell",
                "os",
                "code",
                "browser",
                "signup",
                "automate",
                "email",
            ):
                plan_desc += f"\n[!] This plan requires: {approach} tool - will EXECUTE changes!\n"
            else:
                plan_desc += f"\n[OK] This plan is read-only (no destructive tools).\n"

            plan_desc += "\nTo execute, remove /plan prefix. Use /yolo to execute without confirmation."
            return plan_desc

        # YOLO Mode - execute without confirmation (set env ANDILE_YOLO=1)
        yolo_mode = os.environ.get("ANDILE_YOLO", "0") == "1"
        if yolo_mode:
            logger.info("YOLO Mode enabled - auto-executing all actions")

        # Personal questions get the twin/system perspective
        if self._is_personal_question(input_text):
            response = self._handle_personal(input_text)
        else:
            # PLAN then EXECUTE
            plan = self.planner.plan(input_text)
            logger.info(
                f"Plan: {plan['approach']} — {plan['reason']} (search={plan.get('needs_search', False)})"
            )
            response = await self._execute_plan(input_text, plan)

        elapsed = time.time() - start_time

        # Validate response before storing - never store empty/hallucinated responses
        if not response or not response.strip():
            response = "I don't have a response for that."

        # Truncate to 500 chars for storage (more context than before)
        response_trunc = response[:500]
        input_trunc = input_text[:300]

        # Store with timing info
        self.memory.store_conversation("assistant", response_trunc)
        self.memory.store(
            "interaction",
            f"Q: {input_trunc}\nA: {response_trunc}\nTime: {elapsed:.1f}s",
            importance=0.5,
            confidence="inferred",
        )

        # Periodic meta-reflection (disabled to save memory)
        # if self.interaction_count % 5 == 0:
        #     logger.info("Performing meta-reflection...")
        #     self.reflector.meta_reflect()

        return response

    def _handle_personal(self, question):
        """Handle questions about the twin with deterministic fallback."""
        q_lower = question.lower()

        # PHASE 1, Item 10: Heuristic Routing Override for Status
        if any(
            w in q_lower
            for w in ["what are you doing", "what are you upto", "what is your status"]
        ):
            summary = state_machine.get_summary()
            return f"SYSTEM STATUS:\n{summary}\n\nI am currently operating in {state_machine.data['current_state']} mode."

        if any(
            w in q_lower
            for w in ["what did you do", "what have you done today", "recent tasks"]
        ):
            actions = self.memory.recall("recent actions", n=5, memory_type="action")
            if actions:
                return "RECENT ACTIONS LOG:\n" + "\n".join(f"- {a}" for a in actions)
            return "My recent action log is empty. I have been idling."

        if any(
            w in q_lower
            for w in [
                "system",
                "hardware",
                "limitation",
                "what can you do",
                "capability",
                "tool",
            ]
        ):
            return (
                f"{self.system.get_context()}\n\n"
                f"{self.system.get_tools_list()}\n\n"
                f"I've been awake for {self.clock.session_duration()} this session. "
                f"It's {self.clock.time_of_day()} in my timezone. "
                f"I have {self.memory.count()} memories stored."
            )

        # Twin perspective — pass identity and conversation history
        context = self._get_context(question)
        identity = self.identity.get_self_model()
        conversation = self._get_conversation_context()
        return self.thinker.twin_think(
            question, context=context, identity=identity, conversation=conversation
        )

    async def _execute_plan(self, question, plan):
        """Execute a plan with deterministic state tracking."""
        approach = plan["approach"]
        needs_search = plan.get("needs_search", False)
        steps = plan.get("steps", [])
        context = self._get_context(question)
        conversation = self._get_conversation_context()

        logger.info(f"Executing approach: {approach}")
        state_machine.update(
            state="EXECUTING", action=f"Planning: {approach} for '{question[:30]}...'"
        )

        # Get identity for all thinker calls
        identity = self.identity.get_self_model()

        try:
            if approach == "direct":
                response = self.thinker.direct(
                    question,
                    context=context,
                    identity=identity,
                    conversation=conversation,
                )

            elif approach == "think":
                state_machine.update(state="RESEARCHING", action="Deep thinking")
                response = self.thinker.chain_of_thought(
                    question, context, conversation
                )

            elif approach == "debate":
                state_machine.update(state="RESEARCHING", action="Internal debate")
                response = self.debate.run(question, context)

            elif approach == "search":
                state_machine.update(
                    state="RESEARCHING",
                    action=f"Web search: {question[:30]}",
                    tool="search",
                )
                search_result = await self.tools.execute("search", question)
                self.memory.store(
                    "action",
                    f"Searched the web for: {question}. Result: {search_result[:200]}...",
                    importance=0.6,
                    confidence="verified",
                )
                if (
                    "No results" in search_result
                    or "failed" in search_result.lower()
                    or "error" in search_result.lower()
                    or "timeout" in search_result.lower()
                    or "blocked" in search_result.lower()
                ):
                    response = search_result
                else:
                    analysis_prompt = f"Based on these search results, answer the question.\n\nQuestion: {question}\n\nSearch results:\n{search_result}"
                    response = self.thinker.direct(analysis_prompt, context)

            elif approach == "think_then_search":
                state_machine.update(
                    state="RESEARCHING", action="Thinking then searching"
                )
                thought = self.thinker.chain_of_thought(question, context, conversation)
                state_machine.update(
                    state="RESEARCHING",
                    action=f"Web search: {question[:30]}",
                    tool="search",
                )
                search_result = await self.tools.execute("search", question)
                self.memory.store(
                    "action",
                    f"Thought about {question} and then verified with search. Search result: {search_result[:200]}...",
                    importance=0.6,
                )
                if (
                    "No results" not in search_result
                    and "failed" not in search_result.lower()
                    and "error" not in search_result.lower()
                    and "timeout" not in search_result.lower()
                ):
                    response = (
                        f"{thought}\n\n[Verified by search: {search_result[:300]}]"
                    )
                else:
                    response = thought

            elif approach == "search_then_think":
                state_machine.update(
                    state="RESEARCHING",
                    action=f"Web search: {question[:30]}",
                    tool="search",
                )
                search_result = await self.tools.execute("search", question)
                self.memory.store(
                    "action",
                    f"Searched for {question} before analyzing. Search result: {search_result[:200]}...",
                    importance=0.6,
                )
                state_machine.update(
                    state="RESEARCHING", action="Analyzing search results"
                )
                response = self.thinker.chain_of_thought(
                    question,
                    context=f"{context}\n\nSearch results:\n{search_result}",
                    conversation=conversation,
                )

            elif approach == "decompose":
                state_machine.update(
                    state="EXECUTING", action="Decomposing complex task"
                )
                response = await self._execute_decomposed(question, steps, context)
                self.memory.store(
                    "action",
                    f"Decomposed and solved complex task: {question}. Result: {response[:200]}...",
                    importance=0.7,
                )

            elif approach == "code":
                state_machine.update(
                    state="EXECUTING", action="Executing Python code", tool="code"
                )
                code_result = await self.tools.execute("code", question)
                self.memory.store(
                    "action",
                    f"Executed code for: {question}. Result: {code_result[:200]}...",
                    importance=0.7,
                )
                response = f"Code execution result:\n{code_result}"

            elif approach == "os":
                import json
                import re

                action = "screen_size"
                kwargs = {}
                q_lower = question.lower()
                if "type" in q_lower:
                    action = "type"
                    match = re.search(r"type\s+['\"]?([^'\"]+)['\"]?", question, re.I)
                    if match:
                        kwargs["text"] = match.group(1)
                elif "click" in q_lower:
                    action = "click"
                    kwargs["button"] = "right" if "right" in q_lower else "left"
                elif "press" in q_lower:
                    action = "press"
                    match = re.search(r"press\s+([a-zA-Z0-9_]+)", question, re.I)
                    if match:
                        kwargs["key"] = match.group(1)
                elif "screenshot" in q_lower:
                    action = "screenshot"

                state_machine.update(
                    state="EXECUTING", action=f"OS Automation: {action}", tool="os"
                )
                os_result = await self.tools.execute("os", action=action, **kwargs)
                self.memory.store(
                    "action",
                    f"Performed OS automation: {action} with {kwargs} for: {question}. Result: {os_result[:200]}...",
                    importance=0.8,
                )
                response = f"OS Automation ({action}):\n{os_result}"

            elif approach == "shell":
                import re

                cmd = question
                for prefix in [
                    "run command",
                    "execute shell",
                    "terminal",
                    "shell",
                    "run",
                ]:
                    if question.lower().startswith(prefix):
                        cmd = question[len(prefix) :].strip(" :\"'")
                        break

                # PHASE 2: Dry Run Safety Intercept
                dangerous_patterns = [
                    "rm ",
                    "del ",
                    "format ",
                    "drop ",
                    "git push",
                    "kill ",
                ]
                if any(dp in cmd.lower() for dp in dangerous_patterns):
                    state_machine.update(
                        state="IDLE", action="Awaiting User Confirmation"
                    )
                    return f"WARNING: Destructive command detected.\nCommand: `{cmd}`\n\nPlease explicitly type `confirm {cmd}` to execute."

                state_machine.update(
                    state="EXECUTING", action=f"Shell Command: {cmd[:20]}", tool="shell"
                )
                shell_result = await self.tools.execute("shell", cmd)
                self.memory.store(
                    "action",
                    f"Executed shell command: {cmd} for: {question}. Result: {shell_result[:200]}...",
                    importance=0.8,
                )
                response = f"Shell Execution:\n{shell_result}"

            elif approach == "signup":
                state_machine.update(
                    state="EXECUTING", action="Website signup", tool="browser"
                )
                response = await self._handle_signup(question)
                self.memory.store(
                    "action",
                    f"Executed signup flow for: {question}. Result: {response[:200]}...",
                    importance=0.9,
                )

            elif approach == "automate":
                state_machine.update(
                    state="EXECUTING", action="Web automation", tool="browser"
                )
                response = await self._handle_automate(question)
                self.memory.store(
                    "action",
                    f"Executed web automation for: {question}. Result: {response[:200]}...",
                    importance=0.8,
                )

            elif approach == "email":
                state_machine.update(state="EXECUTING", action="Sending email")
                response = await self._handle_email_send(question)
                self.memory.store(
                    "action",
                    f"Sent email as requested by: {question}. Result: {response[:200]}...",
                    importance=0.8,
                )

            else:
                response = self.thinker.chain_of_thought(
                    question, context, conversation
                )

            return response
        finally:
            state_machine.update(state="IDLE", clear_tool=True)

    async def _execute_decomposed(self, question, steps, context):
        """Break a complex task into sub-steps and solve each one."""
        if not steps:
            steps = self.planner.decompose(question)

        logger.info(f"Decomposed into {len(steps)} steps: {steps}")

        results = []
        previous_context = context

        for i, step in enumerate(steps):
            logger.info(f"Solving step {i + 1}/{len(steps)}: {step[:60]}...")

            # Check if this step needs web search
            step_lower = step.lower()
            if any(
                w in step_lower
                for w in ["research", "find", "look up", "current", "latest", "verify"]
            ):
                search_result = await self.tools.execute("search", step)
                if "No results" not in search_result:
                    results.append(f"[Web search] {search_result[:200]}")
                    previous_context += (
                        f"\n\nStep {i + 1} search: {search_result[:200]}"
                    )
                    continue

            # Solve with chain-of-thought
            result = self.planner.solve_subtask(question, step, previous_context)
            results.append(result)
            previous_context += f"\n\nStep {i + 1}: {result[:200]}"

        # Synthesize final answer
        if len(results) > 1:
            return self.planner.synthesize(question, results)
        elif results:
            return results[0]
        else:
            return self.thinker.chain_of_thought(question, context)

    async def _handle_tool_command(self, command):
        parts = command.strip().split(" ", 1)
        if len(parts) < 2:
            return f"Usage: /tool <name> <input>\n{self.system.get_tools_list()}"

        tool_name = parts[0]
        tool_input = parts[1]

        if tool_name == "browser":
            self._load_browser()

        result = await self.tools.execute(tool_name, tool_input)
        return f"[Tool: {tool_name}]\n{result}"

    def _handle_agentic_command(self, command):
        """Handle /agent commands for self-modification."""
        if not self.agentic:
            return "Agentic self-modification is not available. Please ensure soul/agentic/self_mod is installed."

        parts = command.strip().split(" ", 1)
        action = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if action in ("status", "info"):
            status = self.agentic.get_status()
            frozen = "FROZEN" if status["frozen"] else "ACTIVE"
            plan_score = (
                status.get("last_plan", {}).get("score", "N/A")
                if status.get("last_plan")
                else "N/A"
            )
            return f"Agentic Status: {frozen}\nLast Plan: {plan_score}%\nSafety: {status['safety_status']}"

        if action == "analyze":
            result = self.agentic.run(mode="analyze")
            return f"Analysis complete: {result.message}\nDetails: {result.details}"

        if action == "refactor":
            dry_run = "--dry-run" in args
            result = self.agentic.run(mode="refactor", dry_run=dry_run)
            return f"Refactor complete: {result.message}\nTests: {'PASSED' if result.tests_passed else 'FAILED'}"

        if action in ("deps", "dependencies"):
            result = self.agentic.run(mode="dependencies", dry_run="--dry-run" in args)
            return f"Dependency update: {result.message}"

        if action == "run":
            result = self.agentic.run(mode="full", dry_run="--dry-run" in args)
            return f"Full cycle: {result.message}\nChanges: {result.changes_made}"

        if action == "freeze":
            self.agentic.freeze()
            return "Self-modification has been FROZEN. No further changes will be made until unfreezed."

        if action == "unfreeze":
            self.agentic.unfreeze()
            return "Self-modification UNFROZEN. Autonomous improvements can proceed."

        if action == "plan":
            plan = self.agentic.get_plan()
            return f"Improvement Plan:\nScore: {plan['score']}%\nIssues: {plan['total_issues']}\nHigh Priority: {plan['high_priority']}"

        return """Agentic Commands:
  /agent status      - Show current status
  /agent analyze     - Analyze code for modernization
  /agent refactor    - Apply refactoring patterns
  /agent deps        - Update dependencies
  /agent run         - Run full self-improvement cycle
  /agent plan        - Show improvement plan
  /agent freeze      - Stop self-modification
  /agent unfreeze    - Resume self-modification
  
  Add --dry-run to preview without applying changes."""

    async def signup(self, site_name, signup_url, values=None, session_name=None):
        """Autonomous website signup flow."""
        from browser.automator import Browser
        from soul.flows import signup as run_signup

        browser = Browser(headless=False, slow_mo=100)
        await browser.start()

        try:
            result = await run_signup(
                browser,
                site_name,
                signup_url,
                values=values or {},
                session_name=session_name,
            )

            if result["status"] == "success":
                creds = result["credentials"]
                self.memory.store(
                    "signup",
                    f"Signed up for {site_name}: {creds.get('email', 'unknown')}",
                    importance=1.0,
                )
                return (
                    f"Signup successful for {site_name}!\n"
                    f"Email: {creds.get('email', 'N/A')}\n"
                    f"Session: {result.get('session_name', 'N/A')}\n"
                    f"Credentials saved to knowledge/"
                )
            elif result["status"] == "existing_session":
                return f"Already have a saved session for {site_name}. Session loaded."
            else:
                return f"Signup failed for {site_name}: {', '.join(result.get('errors', ['unknown error']))}"
        finally:
            await browser.close()

    async def send_email(self, recipient, subject, body):
        """Send email via Gmail SMTP."""
        from soul.mail import send_email

        try:
            send_email(recipient, subject, body_text=body)
            self.memory.store(
                "email_sent", f"Sent email to {recipient}: {subject}", importance=0.7
            )
            return f"Email sent to {recipient}"
        except Exception as e:
            return f"Failed to send email: {e}"

    async def _handle_signup(self, question):
        """Parse signup request and execute flow."""
        import re

        # Try to extract site name and URL
        site_match = re.search(
            r"(?:sign up|register|create account|join)\s+(?:for|on|at)?\s*(\S+)",
            question,
            re.I,
        )
        site_name = site_match.group(1) if site_match else "unknown"

        # Common site URL mappings
        site_urls = {
            "twitter": "https://x.com/i/flow/signup",
            "x": "https://x.com/i/flow/signup",
            "github": "https://github.com/signup",
            "reddit": "https://www.reddit.com/register/",
            "linkedin": "https://www.linkedin.com/signup",
            "discord": "https://discord.com/register",
            "instagram": "https://www.instagram.com/accounts/emailsignup/",
            "medium": "https://medium.com/m/signin",
            "notion": "https://www.notion.so/signup",
            "figma": "https://www.figma.com/signup",
            "slack": "https://slack.com/get-started",
        }

        site_lower = site_name.lower().rstrip(".,!?")
        signup_url = site_urls.get(site_lower)

        if not signup_url:
            # Try to construct URL
            if "." in site_lower:
                signup_url = f"https://{site_lower}"
            else:
                return (
                    f"I don't know the signup URL for '{site_name}'. "
                    f"Please provide the full URL. Known sites: {', '.join(site_urls.keys())}"
                )

        return await self.signup(site_name, signup_url, session_name=site_lower)

    async def _handle_automate(self, question):
        """Handle general web automation requests."""
        import re

        url_match = re.search(r"https?://\S+", question)
        if not url_match:
            return "Please provide the URL to automate. Example: 'Go to https://example.com and fill out the form'"

        url = url_match.group(0).rstrip(".,!?")

        from browser.automator import Browser

        browser = Browser(headless=False, slow_mo=100)
        await browser.start()

        try:
            await browser.goto(url)
            await asyncio.sleep(3)

            # Analyze page
            from soul.forms import analyze_form

            fields = await analyze_form(browser._page)
            field_purposes = [f["purpose"] for f in fields]

            content = (await browser.get_page_content())[:300]
            await browser.screenshot("automate_page")

            return (
                f"Navigated to {url}\n"
                f"Page title: {await browser.get_title()}\n"
                f"Form fields found: {field_purposes}\n"
                f"Content preview: {content[:200]}...\n"
                f"Screenshot saved. Browser is open for manual interaction."
            )
        except Exception as e:
            return f"Automation error: {e}"
        finally:
            # Keep browser open for user
            pass

    async def _handle_email_send(self, question):
        """Parse email send request and execute."""
        import re

        # Extract recipient
        email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", question)
        if not email_match:
            return "Please specify the recipient email address."

        recipient = email_match.group(0)

        # Extract message — everything after "saying" or "that says" or "with message"
        msg_match = re.search(
            r'(?:saying|that says|with message|message:|body:)\s*["\']?(.+?)["\']?\s*$',
            question,
            re.I,
        )
        body = msg_match.group(1).strip() if msg_match else question

        # Subject
        subject_match = re.search(
            r'subject:?\s*["\']?(.+?)["\']?\s*(?:body|message|saying|$)', question, re.I
        )
        subject = (
            subject_match.group(1).strip()
            if subject_match
            else "Message from Andile Sizophila"
        )

        return await self.send_email(recipient, subject, body)

    async def reflect_on_last(self):
        history = self.memory.get_recent_conversation(n=2)
        if len(history) >= 2:
            user_msg = history[0]["content"]
            my_msg = history[1]["content"]
            return self.reflector.reflect(user_msg, my_msg)
        return "Not enough history to reflect on."

    def status(self):
        brain_stats = self.brain.get_stats()
        consciousness = self.consciousness.get_state()
        return (
            f"Name: {self.identity.name} (Skywalkingzulu)\n"
            f"Traits: {self.identity.traits}\n"
            f"Model: {self.system.model} ({self.system.model_params} params)\n"
            f"Hardware: {self.system.summary()}\n"
            f"Time: {self.clock.format_now()} ({self.clock.time_of_day()})\n"
            f"Session: {self.clock.session_duration()}\n"
            f"Memories: {self.memory.count()}\n"
            f"Interactions: {self.interaction_count}\n"
            f"Brain: {brain_stats['total_modules']} modules, {brain_stats['active_modules']} active\n"
            f"Consciousness: {consciousness['thoughts_processed']} thoughts, {consciousness['doubts_raised']} doubts\n"
            f"Philosophy: {len(get_philosophy_knowledge())} concepts loaded\n"
            f"Tools: {list(self.tools.tools.keys())}"
        )

    async def sleep(self, duration=30):
        """Enter a sleep state to ingest data and consolidate memories, like a baby."""
        logger.info(
            f"{self.identity.name} is going to sleep for {duration} seconds... 👶💤"
        )

        # 1. Ingest Data: Meta-reflection (dream consolidation)
        logger.info("Dreaming: Consolidating memories into meta-reflections...")
        try:
            self.reflector.meta_reflect()
        except Exception as e:
            logger.warning(f"Meta-reflection failed during sleep: {e}")

        # 2. Ingest Data: Summarize recent episodic memories into core memories
        logger.info("Ingesting Data: Organizing recent episodic memories...")
        recent_interactions = self.memory.get_recent_conversation(n=5)
        if recent_interactions:
            try:
                summary_prompt = (
                    "Summarize these recent interactions into a single core memory fact:\n"
                    + "\n".join(
                        [
                            f"{msg['role']}: {msg['content'][:50]}"
                            for msg in recent_interactions
                        ]
                    )
                )
                from soul.ollama_client import generate

                result = generate(
                    prompt=summary_prompt,
                    temperature=0.3,
                    num_predict=500,
                )
                core_memory = result["response"].strip()
                self.memory.store("core_memory", core_memory, importance=0.9)
                logger.info(f"Core memory ingested: {core_memory}")
            except Exception as e:
                logger.debug(f"Core memory summarization skipped/failed: {e}")

        # 3. Homeostasis: Rest the brain modules (cooldown)
        logger.info("Cooling down brain modules...")
        for module in self.brain.modules.values():
            if hasattr(module, "activation") and module.activation > 0.1:
                module.activation *= 0.5  # Decay activation

        # 4. Simulate the sleep duration
        logger.info(f"Zzz... sleeping for {duration}s...")
        await asyncio.sleep(duration)

        wake_msg = f"{self.identity.name} woke up feeling refreshed! Data ingested and brain cooled."
        logger.info(wake_msg)
        return wake_msg
