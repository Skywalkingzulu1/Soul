import asyncio
import sys
import os
import logging
import signal

# Force UTF-8 encoding for stdout
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(__file__))
from soul.philosophy.knowledge import search_philosophy

logging.basicConfig(
    level=logging.INFO,
    format="[%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("ANDILE")


def print_banner(soul):
    print()
    print("=" * 60)
    print(f"  Digital Twin Online: {soul.identity.name}")
    print(f"  Moniker: Skywalkingzulu")
    print(f"  Traits: {soul.identity.traits}")
    print(f"  Memories: {soul.memory.count()}")
    print("=" * 60)
    print()
    print("  Commands:")
    print("    /status               - Show twin status")
    print("    /reflect              - Reflect on last interaction")
    print("    /think <question>     - Deep chain-of-thought")
    print("    /debate <question>    - Multi-agent debate")
    print("    /philosophy <topic>   - Philosophical analysis")
    print("    /dialectic <concept>  - Thesis-antithesis-synthesis")
    print("    /search <query>       - Quick DuckDuckGo search")
    print("    /plan <task>         - Show plan without executing (like Gemini)")
    print("    /browser <url>        - Open browser to URL")
    print("    /signup <site>        - Sign up for a website")
    print("    /email <to> <message> - Send email via Gmail")
    print("    /sleep [seconds]      - Go to sleep and ingest data")
    print("    /teach <knowledge>   - Learn new knowledge/patterns")
    print("  Codebase Tools:")
    print("    glob <pattern>        - Find files matching pattern")
    print("    grep <term>           - Search files for term")
    print("    read_file <path>     - Read a file")
    print("    ls [path]             - List directory")
    print("    /sessions             - List saved login sessions")
    print("    exit / quit / bye     - End session")
    print()
    print("  Or just talk naturally — I'll figure out what to do.")


async def main():
    from server import start_ollama
    from soul.brain import Soul

    logger.info("Starting ollama server...")
    start_ollama()

    soul = Soul(name="Andile Sizophila Mchunu")
    print_banner(soul)

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{soul.identity.name}: Goodbye. I will remember this.")
            break

        if not user_input:
            continue

        command = user_input.strip()
        command_lower = command.lower()

        # Fix common typos in commands
        if command_lower.startswith("/philsophy") or command_lower.startswith(
            "/philosopy"
        ):
            user_input = (
                "/philosophy " + user_input[command_lower.find(" ") + 1 :]
                if " " in user_input
                else "/philosophy"
            )
            command = user_input
            command_lower = "philosophy"

        if command_lower in ("exit", "quit", "bye"):
            print(
                f"\n{soul.identity.name}: Goodbye. I will remember this conversation."
            )
            break

        if command_lower == "/status":
            print(f"\n{soul.identity.name}: {soul.status()}\n")
            continue

        if command_lower == "/reflect":
            reflection = await soul.reflect_on_last()
            print(f"\n{soul.identity.name} [reflecting]: {reflection}\n")
            continue

        if command_lower.startswith("/think "):
            question = user_input[7:]
            context = soul._get_context(question)
            response = soul.thinker.chain_of_thought(question, context)
            print(f"\n{soul.identity.name}: {response}\n")
            soul.memory.store_conversation("assistant", response)
            continue

        if command_lower.startswith("/debate "):
            question = user_input[8:]
            context = soul._get_context(question)
            response = soul.debate.run(question, context)
            print(f"\n{soul.identity.name} [debate]: {response}\n")
            soul.memory.store_conversation("assistant", response)
            continue

        if command_lower.startswith("/philosophy "):
            topic = user_input[12:]
            results = search_philosophy(topic, n=3)
            print(f"\n{soul.identity.name} [philosophy]:")
            for r in results:
                print(
                    f"  [{r['weight']:.1f}] {r['philosopher']:12} | {r['branch']:15} | {r['concept'][:80]}"
                )
            print()
            soul.consciousness.log_thought("philosophy", f"Explored: {topic}")
            continue

        if command_lower.startswith("/dialectic "):
            concept = user_input[11:]
            result = soul.dialectic.full_dialectic(concept)
            print(f"\n{soul.identity.name} [dialectic]:")
            print(f"  THESIS: {result['thesis']['position']}")
            print(f"  ANTITHESIS: {result['antithesis']['position']}")
            print(f"  SYNTHESIS: {result['synthesis']['synthesis']}")
            print(f"  QUESTIONS: {', '.join(result['socratic_questions'][:3])}")
            print()
            soul.consciousness.log_thought("dialectic", f"Debated: {concept}")
            continue

        if command_lower.startswith("/search "):
            query = user_input[8:]
            result = await soul.tools.execute("search", query)
            print(f"\n{soul.identity.name} [search]: {result}\n")
            continue

        # /plan command - show plan without executing
        if command_lower.startswith("/plan "):
            question = user_input[6:].strip()
            plan = soul.planner.plan(question)
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

            plan_desc += "\nTo execute, remove /plan prefix."
            print(f"\n{soul.identity.name} [plan]: {plan_desc}\n")
            continue

        if command_lower.startswith("/browser ") or command_lower.startswith(
            "/browse "
        ):
            url = user_input[9:].strip()
            if not url.startswith("http"):
                url = "https://" + url
            print(f"\nOpening browser to {url}...")
            from browser.automator import Browser

            browser = Browser(headless=False, slow_mo=100)
            try:
                await browser.start()
                await browser.goto(url)
                title = await browser.get_title()
                content = (await browser.get_page_content())[:300]
                print(f"\n{soul.identity.name} [browser]: {title}\n{content}\n")
                await browser.screenshot("browser_visit")
                input("Press Enter to close browser...")
            finally:
                await browser.close()
            continue

        if command_lower.startswith("/research "):
            query = user_input[10:]
            print(f"\nResearching: {query}...")
            from browser.automator import Browser

            browser = Browser(headless=False, slow_mo=100)
            try:
                await browser.start()
                results = await browser.research(query)
                print(f"\n{soul.identity.name} [research]:")
                for i, r in enumerate(results[:3], 1):
                    print(f"  {i}. {r[:150]}")
                print()
                await browser.screenshot("research_result")
                input("Press Enter to close browser...")
            finally:
                await browser.close()
            continue

        if command_lower.startswith("/signup "):
            site = user_input[8:].strip()
            print(f"\nSigning up for {site}...")
            site_urls = {
                "twitter": "https://x.com/i/flow/signup",
                "x": "https://x.com/i/flow/signup",
                "github": "https://github.com/signup",
                "reddit": "https://www.reddit.com/register/",
                "linkedin": "https://www.linkedin.com/signup",
                "discord": "https://discord.com/register",
                "medium": "https://medium.com/m/signin",
                "figma": "https://www.figma.com/signup",
            }
            url = site_urls.get(site.lower(), f"https://{site.lower()}")
            result = await soul.signup(site, url)
            print(f"\n{soul.identity.name}: {result}\n")
            continue

        if command_lower.startswith("/email "):
            parts = user_input[7:].strip().split(" ", 1)
            if len(parts) < 2:
                print("\nUsage: /email <recipient> <message>\n")
                continue
            recipient = parts[0]
            message = parts[1]
            result = await soul.send_email(
                recipient, "Message from Andile Sizophila", message
            )
            print(f"\n{soul.identity.name}: {result}\n")
            continue

        if command_lower.startswith("/sleep"):
            duration = 30
            parts = user_input.split(" ")
            if len(parts) > 1:
                try:
                    duration = int(parts[1])
                except:
                    # Check for "2 hours" etc
                    if "hour" in user_input:
                        try:
                            duration = int(parts[1]) * 3600
                        except:
                            pass

            print(
                f"\n{soul.identity.name}: Starting sleep cycle for {duration} seconds..."
            )
            wake_msg = await soul.sleep(duration)
            print(f"\n{soul.identity.name}: {wake_msg}\n")
            continue

        if command_lower.startswith("/teach "):
            knowledge = user_input[7:].strip()
            if knowledge:
                soul.memory.store("knowledge", knowledge, importance=0.9)
                print(f"\n{soul.identity.name}: I've learned: {knowledge[:100]}...\n")
            else:
                print(
                    f"\n{soul.identity.name}: What would you like me to learn? Usage: /teach <knowledge>\n"
                )
            continue

        if command == "/sessions":
            from soul.session import list_sessions

            sessions = list_sessions()
            if sessions:
                print(f"\n  Saved sessions ({len(sessions)}):")
                for s in sessions:
                    print(
                        f"    {s['name']:20} | {s.get('saved_at_readable', 'unknown')} | {s.get('cookies_count', 0)} cookies"
                    )
            else:
                print("\n  No saved sessions.")
            print()
            continue

        # Code tool commands (like Gemini CLI)
        if command_lower.startswith("glob "):
            pattern = user_input[5:].strip()
            result = await soul.tools.execute("glob", pattern)
            print(f"\n{soul.identity.name} [glob]: {result}\n")
            continue

        if command_lower.startswith("grep "):
            parts = user_input[5:].strip().split(" ", 1)
            if len(parts) >= 2:
                result = await soul.tools.execute("grep", parts[0], parts[1])
            else:
                result = await soul.tools.execute("grep", parts[0])
            print(f"\n{soul.identity.name} [grep]: {result}\n")
            continue

        if command_lower.startswith("read_file ") or command_lower.startswith("cat "):
            # Handle both read_file and cat
            if command_lower.startswith("cat "):
                filepath = user_input[4:].strip()
            else:
                filepath = user_input[10:].strip()
            result = await soul.tools.execute("read_file", filepath)
            print(f"\n{soul.identity.name} [read_file]: {result}\n")
            continue

        if command_lower.startswith("ls "):
            path = user_input[3:].strip() or None
            result = await soul.tools.execute("ls", path)
            print(f"\n{soul.identity.name} [ls]: {result}\n")
            continue

        # Normal conversation
        try:
            response = await soul.perceive(user_input)
            print(f"\n{soul.identity.name}: {response}\n")
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"\n[Error: {e}]\n")


if __name__ == "__main__":
    asyncio.run(main())
