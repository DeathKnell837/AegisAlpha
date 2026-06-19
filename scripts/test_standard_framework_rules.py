import urllib.request
import json
import time
import sys

# Endpoints
BASE_URL = "https://lexaudit-wfmf.onrender.com"
RESET_URL = f"{BASE_URL}/reset"
SEND_URL = f"{BASE_URL}/send-message?room_id=15c71300-086d-4f1d-a6f2-a14fc04e398d"
EVENTS_URL = f"{BASE_URL}/events.json"

# Standard guidelines mock (matching frontend implementation)
gdpr_rules = """GDPR Reference Guidelines (Including EU-US Data Privacy Framework):
- GDPR-RULE-01 (Data Processing Agreement): Under GDPR Article 28, contracts involving personal data processing must specify the subject matter, duration, nature, and purpose of processing, the type of personal data, categories of data subjects, and the obligations/rights of the controller.
- GDPR-RULE-02 (Security of Processing): Requires implementation of appropriate technical and organizational measures to ensure a level of security appropriate to the risk, including encryption and pseudonymization.
- GDPR-RULE-03 (International Transfers): Personal data transfers outside the EEA require Standard Contractual Clauses (SCCs), adequacy decisions, or certification under the EU-US Data Privacy Framework (DPF) for US entities.
- GDPR-RULE-04 (Liability Caps): Limits on liability must not restrict statutory rights to compensation for data protection breaches under Article 82."""

ccpa_rules = """CCPA/CPRA Reference Guidelines (Latest Regulations):
- CCPA-RULE-01 (Service Provider Obligations): Service provider contracts must prohibit selling/sharing personal information, retaining/using/disclosing personal information for any purpose other than performing the business services, or combining it with other information.
- CCPA-RULE-02 (Opt-Out Support): Service providers must cooperate with the business to honor consumer opt-outs from selling/sharing personal information and requests to limit the use of sensitive personal information.
- CCPA-RULE-03 (Audit and Compliance Rights): Must allow the business to conduct reasonable audits and assessments to monitor service provider compliance."""

# Load sample contract
print("Loading contract...")
try:
    with open("sample_contract.txt", "r", encoding="utf-8") as f:
        contract_text = f.read().strip()
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

# Step 2: Construct and send payload (simulating frontend sending GDPR and CCPA standard guidelines)
print("\nStep 2: Sending audit request with preloaded GDPR & CCPA reference rules...")
combined_rules = f"{gdpr_rules}\n\n{ccpa_rules}"
message_content = (
    "@rogiebacanto2002/planner-agent Please audit the following contract for compliance against GDPR, CCPA/CPRA "
    "and the provided reference rules.\n\n"
    f"REFERENCE RULES:\n{combined_rules}\n\n"
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
    sys.exit(1)
