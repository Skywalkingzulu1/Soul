import os
import json
import time
import logging
from bs4 import BeautifulSoup
import requests
import re
import random

from soul.ollama_client import generate

from soul.app_library import APP_LIBRARY
from soul.state import state_machine
from soul.big_brother import BigBrother

logger = logging.getLogger("APP_FACTORY")

# The directory where the mega-repo will live locally
FACTORY_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "NEPTUNE-Utility-Grid"
)

APP_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Fira+Code&display=swap" rel="stylesheet">
    <style>
        :root {{ --bg: #050505; --text: #e2e8f0; --accent: #3b82f6; --card: #111111; --border: #222; }}
        body {{ font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; line-height: 1.6; border-top: 4px solid var(--accent); }}
        header {{ background: var(--card); padding: 2rem 1rem; text-align: center; border-bottom: 1px solid var(--border); }}
        h1 {{ color: white; margin: 0; font-size: 2.2rem; font-weight: 800; letter-spacing: -1px; }}
        .subtitle {{ color: #64748b; font-size: 1rem; margin-top: 0.5rem; }}
        main {{ max-width: 900px; margin: 3rem auto; padding: 0 1.5rem; }}
        .ad-space {{ background: #000; border: 1px dashed #333; height: 90px; display: flex; align-items: center; justify-content: center; color: #444; margin: 2rem 0; border-radius: 8px; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 2px; }}
        .app-container {{ background: var(--card); padding: 2.5rem; border-radius: 12px; border: 1px solid var(--border); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); }}
        .seo-content {{ margin-top: 4rem; padding-top: 2rem; border-top: 1px solid var(--border); color: #94a3b8; }}
        .seo-content h2 {{ color: white; font-size: 1.2rem; }}
        input, button, textarea, select {{ padding: 0.8rem; border-radius: 6px; border: 1px solid #333; background: #000; color: white; width: 100%; margin-bottom: 1.2rem; box-sizing: border-box; font-family: 'Fira Code', monospace; font-size: 0.9rem; }}
        input:focus {{ border-color: var(--accent); outline: none; }}
        button {{ background: var(--accent); cursor: pointer; font-weight: 800; border: none; transition: all 0.2s; text-transform: uppercase; letter-spacing: 1px; }}
        button:hover {{ background: #2563eb; transform: translateY(-2px); }}
        #result {{ margin-top: 1.5rem; padding: 1.5rem; background: #000; border-radius: 8px; display: none; border-left: 4px solid var(--accent); font-family: 'Fira Code', monospace; font-size: 0.95rem; line-height: 1.4; overflow-x: auto; }}
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
        label {{ display: block; margin-bottom: 0.5rem; font-size: 0.7rem; font-weight: 800; color: #475569; text-transform: uppercase; letter-spacing: 1px; }}
    </style>
</head>
<body>
    <header>
        <h1>{h1_title}</h1>
        <p class="subtitle">{subtitle}</p>
    </header>

    <main>
        <div class="ad-space" id="ad-space-top">Advertisement</div>

        <div class="app-container">
            {html_ui}
            <div id="result"></div>
        </div>

        <article class="seo-content">
            <h2>Technical Overview</h2>
            <p>{seo_article}</p>
        </article>

        <div class="ad-space" id="ad-space-bottom">Advertisement</div>
    </main>

    <script>
        {js_logic}
    </script>
</body>
</html>"""


class AppFactory:
    """Generates 10/10 SEO apps with internal Big Brother auditing."""

    def __init__(self, model="gpt-oss:120b-cloud") -> None:
        self.model = model
        self.overseer = BigBrother(FACTORY_DIR)
        if not os.path.exists(FACTORY_DIR):
            os.makedirs(FACTORY_DIR)
        self.monetization_setup()

    def monetization_setup(self) -> None:
        """Prepare ads.txt and robots.txt."""
        ads_txt = "# Neptune Utility Grid Monetization\n# Add your AdSense / Affiliate IDs here\n"
        robots_txt = "User-agent: *\nAllow: /\nSitemap: https://skywalkingzulu1.github.io/NEPTUNE-Utility-Grid/sitemap.xml"
        with open(os.path.join(FACTORY_DIR, "ads.txt"), "w") as f:
            f.write(ads_txt)
        with open(os.path.join(FACTORY_DIR, "robots.txt"), "w") as f:
            f.write(robots_txt)

    def generate_sitemap(self) -> None:
        """Update sitemap.xml and the portal index."""
        files = [
            f
            for f in os.listdir(FACTORY_DIR)
            if f.endswith(".html") and f != "index.html"
        ]
        base_url = "https://skywalkingzulu1.github.io/NEPTUNE-Utility-Grid/"
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for f in files:
            sitemap += (
                f"  <url><loc>{base_url}{f}</loc><priority>0.8</priority></url>\n"
            )
        sitemap += "</urlset>"
        with open(os.path.join(FACTORY_DIR, "sitemap.xml"), "w") as f:
            f.write(sitemap)
        self.update_index(files)

    def update_index(self, files) -> None:
        """Generate a high-fidelity SaaS-style portal."""
        links_html = ""
        for f in files:
            name = f.replace(".html", "").replace("-", " ").title()
            links_html += f"""
            <li class="tool-card">
                <span class="category">Utility</span>
                <a href="{f}">{name}</a>
                <p>High-performance web tool by Neptune.</p>
            </li>"""

        portal_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEPTUNE Utility Grid</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background: #050505; color: white; margin: 0; padding: 0; }}
        .nav {{ padding: 2rem; border-bottom: 1px solid #111; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-weight: 900; font-size: 1.5rem; letter-spacing: -1px; }}
        .hero {{ padding: 5rem 2rem; text-align: center; background: radial-gradient(circle at center, #111 0%, #050505 100%); }}
        .hero h1 {{ font-size: 4rem; font-weight: 900; margin: 0; letter-spacing: -2px; background: linear-gradient(to right, #3b82f6, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .hero p {{ color: #64748b; font-size: 1.2rem; margin-top: 1rem; }}
        .container {{ max-width: 1100px; margin: 0 auto; padding: 4rem 2rem; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem; list-style: none; padding: 0; }}
        .tool-card {{ background: #0a0a0a; border: 1px solid #1a1a1a; padding: 2rem; border-radius: 12px; transition: all 0.3s; }}
        .tool-card:hover {{ border-color: #3b82f6; transform: translateY(-5px); box-shadow: 0 20px 40px -15px rgba(59, 130, 246, 0.3); }}
        .tool-card .category {{ font-size: 0.6rem; font-weight: 900; color: #3b82f6; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 1rem; display: block; }}
        .tool-card a {{ color: white; text-decoration: none; font-size: 1.25rem; font-weight: 700; display: block; margin-bottom: 0.5rem; }}
        .tool-card p {{ color: #475569; font-size: 0.85rem; margin: 0; }}
        footer {{ padding: 4rem; text-align: center; border-top: 1px solid #111; color: #333; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 3px; }}
    </style>
</head>
<body>
    <div class="nav"><div class="logo">NEPTUNE GRID</div><div style="color:#333">v1.0.4-AUTONOMOUS</div></div>
    <div class="hero">
        <h1>THE UTILITY GRID</h1>
        <p>1,000+ Verified Micro-Applications. 10/10 Functional Integrity.</p>
    </div>
    <div class="container">
        <ul class="grid">{links_html}</ul>
    </div>
    <footer>Azania Neptune Labs &copy; 2026</footer>
</body>
</html>"""
        with open(os.path.join(FACTORY_DIR, "index.html"), "w") as f:
            f.write(portal_html)

    def fetch_trends(self) -> None:
        return random.sample(APP_LIBRARY, 1)[0]

    def generate_seo_content(self, app_def) -> None:
        modifiers = ["Pro", "Suite", "Master", "Edge", "Cloud", "Nexus", "Prime"]
        long_tail = (
            f"{app_def['id'].replace('-', ' ').title()} {random.choice(modifiers)}"
        )
        prompt = (
            f"You are a professional technical writer.\n"
            f"Write SEO metadata for a high-end web utility: '{long_tail}'.\n"
            f"Provide exactly this format:\n"
            "TITLE: [SEO Title]\nDESC: [Description]\nKEYS: [Keywords]\nH1: [Heading]\nSUB: [Subtitle]\nARTICLE: [Detailed 100-word article]"
        )
        try:
            response = generate(prompt=prompt, temperature=0.4)
            text = response["response"].strip()
            data = {
                "slug": long_tail.replace(" ", "-").lower(),
                "html_ui": app_def["ui"],
                "js_logic": app_def["js"],
            }
            for line in text.split("\n"):
                if line.startswith("TITLE:"):
                    data["title"] = line.replace("TITLE:", "").strip()
                elif line.startswith("DESC:"):
                    data["description"] = line.replace("DESC:", "").strip()
                elif line.startswith("KEYS:"):
                    data["keywords"] = line.replace("KEYS:", "").strip()
                elif line.startswith("H1:"):
                    data["h1_title"] = line.replace("H1:", "").strip()
                elif line.startswith("SUB:"):
                    data["subtitle"] = line.replace("SUB:", "").strip()
                elif line.startswith("ARTICLE:"):
                    data["seo_article"] = line.replace("ARTICLE:", "").strip()
            return data
        except Exception:
            return None

    def build_app(self, app_def) -> None:
        data = self.generate_seo_content(app_def)
        if not data:
            return False
        try:
            html = APP_TEMPLATE.format(
                title=data.get("title", "Neptune Tool"),
                description=data.get("description", "Premium utility."),
                keywords=data.get("keywords", "utility, grid"),
                h1_title=data.get("h1_title", "Neptune Tool"),
                subtitle=data.get("subtitle", "High-performance tool."),
                html_ui=data["html_ui"],
                js_logic=data["js_logic"],
                seo_article=data.get(
                    "seo_article", "Verified utility logic by Neptune Labs."
                ),
            )
            file_path = os.path.join(FACTORY_DIR, f"{data['slug']}.html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)
            return True
        except Exception:
            return False

    def run_batch(self, count=5) -> None:
        """Execute batch then CONSULT THE OVERSEER (Big Brother)."""
        successes = 0
        for i in range(count):
            if self.build_app(self.fetch_trends()):
                successes += 1

        if successes > 0:
            self.generate_sitemap()

            # Big Brother Consult (Phase 10 Mandatory Step)
            passed, report = self.overseer.audit()
            if passed:
                logger.info(f"Big Brother Audit PASSED: {report}")
                self.overseer.deploy()
            else:
                logger.error(f"Big Brother Audit FAILED: {report}")
                state_machine.update(state="ERROR", action="Overseer Rejected Batch")
        return successes
