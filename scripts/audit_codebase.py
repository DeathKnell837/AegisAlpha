# scripts/audit_codebase.py
import os
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def load_file_content(relative_path: str) -> str:
    filepath = ROOT_DIR / relative_path
    if not filepath.exists():
        return f"[FILE NOT FOUND: {relative_path}]"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"[ERROR READING FILE {relative_path}: {e}]"

def main():
    load_dotenv(str(ROOT_DIR / ".env"))
    api_key = os.getenv("AIMLAPI_KEY")
    if not api_key:
        print("Error: AIMLAPI_KEY is not set in your .env file!")
        sys.exit(1)

    print("Reading files for audit...")
    files_to_audit = [
        "src/agent_factory.py",
        "src/visual_logger.py",
        "src/models.py",
        "src/config.py",
        "src/prompts.py",
        "web/index.html",
        "web/index.css",
        "web/index.js",
        "scripts/run_all.py",
        "agent_config.yaml"
    ]

    bundle = ""
    for rel_path in files_to_audit:
        content = load_file_content(rel_path)
        bundle += f"\n\n=================== FILE: {rel_path} ===================\n{content}\n"

    print("Initializing OpenAI client with AI/ML API base url...")
    client = OpenAI(
        base_url="https://api.aimlapi.com/v1",
        api_key=api_key
    )

    prompt = (
        "You are Claude Opus 4.8, the most powerful AI model. You are auditing a Band of Agents hackathon project "
        "built under the 'Regulated & High-Stakes Workflows' track.\n\n"
        "Here is the current implementation bundle:\n"
        f"{bundle}\n\n"
        "Your task is to analyze the codebase for:\n"
        "1. Band SDK integration bugs (e.g., mention formats, tool names, context isolation violations).\n"
        "2. Loop risks (e.g., infinite back-and-forth loops, incorrect message routing).\n"
        "3. HTML/CSS/JS dashboard errors (e.g., missing metrics, script errors, incorrect visual mapping updates).\n"
        "4. Any other logic bugs, missing features, or configuration inconsistencies.\n\n"
        "Format your output as a comprehensive Markdown report. If you find any issues, provide "
        "exact code corrections/diffs for the affected files so that they can be easily fixed."
    )

    print("Sending codebase to Claude-Opus-4-8 for a thorough audit...")
    try:
        response = client.chat.completions.create(
            model="claude-opus-4-8",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        report = response.choices[0].message.content
        
        # Save report
        report_path = ROOT_DIR / "claude_audit_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
            
        print(f"\nAudit completed! Report saved to {report_path}")
        print("\n--- REPORT SUMMARY ---")
        print(report[:1500] + "\n... (truncated, check claude_audit_report.md for full report) ...")
        
    except Exception as e:
        print(f"Error during audit: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
