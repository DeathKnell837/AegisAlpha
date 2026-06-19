import urllib.request
import json
import time
import sys

# Endpoints
BASE_URL = "https://lexaudit-wfmf.onrender.com"
RESET_URL = f"{BASE_URL}/reset"
SEND_URL = f"{BASE_URL}/send-message?room_id=15c71300-086d-4f1d-a6f2-a14fc04e398d"
EVENTS_URL = f"{BASE_URL}/events.json"

# Load files
print("Loading contract and custom rules...")
try:
    with open("sample_contract.txt", "r", encoding="utf-8") as f:
        contract_text = f.read().strip()
    with open("sample_rules.txt", "r", encoding="utf-8") as f:
        rules_text = f.read().strip()
except Exception as e:
    print(f"Error loading files: {e}")
    sys.exit(1)

# Step 1: Reset Render backend log
print("\nStep 1: Resetting Render backend event log...")
try:
    req = urllib.request.Request(RESET_URL, data=b"", headers={'User-Agent': 'Mozilla/5.0'}, method='POST')
    with urllib.request.urlopen(req, timeout=10) as resp:
        print("Reset response:", resp.read().decode('utf-8'))
except Exception as e:
    print(f"Reset failed: {e}")
    sys.exit(1)

# Step 2: Construct and send payload
print("\nStep 2: Sending audit request with custom reference rules...")
frameworks = "GDPR, CCPA/CPRA, HIPAA, SOC 2, SOX, AML/KYC"
message_content = (
    f"@rogiebacanto2002/planner-agent Please audit the following contract for compliance against {frameworks} "
    f"and the provided reference rules.\n\n"
    f"REFERENCE RULES:\n{rules_text}\n\n"
    f"CONTRACT NAME: sample_contract\n\n"
    f"CONTRACT TEXT:\n{contract_text}"
)

payload = {
    "content": message_content,
    "mentions": ["@rogiebacanto2002/planner-agent"]
}

try:
    data_bytes = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(SEND_URL, data=data_bytes, headers={
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }, method='POST')
    with urllib.request.urlopen(req, timeout=15) as resp:
        print("Message sent successfully. Response:", resp.read().decode('utf-8'))
except Exception as e:
    print(f"Failed to send audit request: {e}")
    sys.exit(1)

# Step 3: Poll event log until review completes
print("\nStep 3: Polling agent pipeline execution...")
processed_sigs = set()
review_completed = False
start_time = time.time()
max_wait = 240 # 4 minutes max

while time.time() - start_time < max_wait:
    try:
        req = urllib.request.Request(f"{EVENTS_URL}?t={int(time.time())}", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            events = json.loads(resp.read().decode('utf-8'))
            
            for ev in events:
                sig = f"{ev.get('timestamp')}_{ev.get('agent')}_{ev.get('type')}"
                if sig not in processed_sigs:
                    processed_sigs.add(sig)
                    agent = ev.get('agent', 'unknown').upper()
                    ev_type = ev.get('type', 'unknown')
                    content = ev.get('content', '')
                    
                    if ev_type == "thinking":
                        print(f"\n[{agent}] is thinking...")
                    elif ev_type == "message":
                        print(f"\n[{agent}] sent a message:")
                        print("-" * 50)
                        print(content)
                        print("-" * 50)
                    elif ev_type == "event":
                        msg_type = ev.get('message_type')
                        print(f"\n[SYSTEM EVENT] {msg_type.upper()}")
                        if msg_type == "compliance_review_completed":
                            review_completed = True
                            meta = ev.get("metadata", {})
                            print(f"Final Verdict: {meta.get('verdict')}")
                            print(f"Risk Score: {meta.get('risk_score')}/100")
                            
        if review_completed:
            print("\nAudit completed successfully!")
            break
            
    except Exception as e:
        print(f"Polling warning: {e}")
        
    time.sleep(5)

if not review_completed:
    print("\nAudit timed out before Reviewer agent completed.")
