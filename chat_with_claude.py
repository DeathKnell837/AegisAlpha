# chat_with_claude.py
# An interactive CLI to chat with the claude-opus-4-8 model on AI/ML API.
# Automatically injects your hackathon guides and configs into the context.

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

def load_workspace_context():
    context = ""
    files_to_read = {
        "HACKATHON_GUIDE.md": "c:/Users/USER/Desktop/HACKATHON/HACKATHON_GUIDE.md",
        "HACKATHON_CHECKLIST.md": "c:/Users/USER/Desktop/HACKATHON/HACKATHON_CHECKLIST.md",
        "agent_config.yaml": "c:/Users/USER/Desktop/HACKATHON/agent_config.yaml"
    }
    
    for name, path in files_to_read.items():
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    context += f"\n=== FILE: {name} ===\n{content}\n"
            except Exception as e:
                print(f"Warning: Could not read {name}: {e}")
    return context

def main():
    load_dotenv("c:/Users/USER/Desktop/HACKATHON/.env")
    api_key = os.getenv("AIMLAPI_KEY")
    
    if not api_key:
        print("Error: AIMLAPI_KEY is not set in your .env file!")
        sys.exit(1)
        
    print("Initializing client...")
    client = OpenAI(
        base_url="https://api.aimlapi.com/v1",
        api_key=api_key
    )
    
    print("Reading workspace context files...")
    workspace_context = load_workspace_context()
    
    system_prompt = (
        "You are an expert software architect and assistant helping the user design and plan "
        "their Band of Agents hackathon project.\n\n"
        "Here is the context of the user's workspace, guidelines, checklist, and registered agents:\n"
        f"{workspace_context}\n"
        "You must answer user questions, brainstorm ideas, and draft implementation plans. "
        "Keep your suggestions highly actionable, and optimize for the free tiers of Featherless.ai "
        "and AI/ML API."
    )
    
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    print("\n======================================================================")
    print("      Welcome to the Hackathon Planning Chat (claude-opus-4-8)        ")
    print("======================================================================")
    print("Claude is fully aware of your guides, checklist, and registered agents.")
    print("Type your message and press Enter. Type 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("You > ")
            if user_input.strip().lower() == "exit":
                print("Goodbye!")
                break
                
            if not user_input.strip():
                continue
                
            messages.append({"role": "user", "content": user_input})
            
            print("Claude > ", end="", flush=True)
            
            # Stream the response
            stream = client.chat.completions.create(
                model="claude-opus-4-8",
                messages=messages,
                stream=True
            )
            
            assistant_response = ""
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    print(content, end="", flush=True)
                    assistant_response += content
            print("\n")
            
            messages.append({"role": "assistant", "content": assistant_response})
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    main()
