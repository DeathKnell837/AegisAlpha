import urllib.request
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT_DIR / "sample_contract.txt"

def main():
    print("Reading sample contract...")
    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        contract_text = f.read()

    # Read configuration keys
    from dotenv import load_dotenv
    import os
    load_dotenv(dotenv_path=str(ROOT_DIR / ".env"))

    room_id = "821e2186-0fd1-42e4-9ba8-8e468f3b6c0c"
    api_key = os.getenv("PLANNER_API_KEY", "band_a_1781282587_R_qQWK_569pK8JHbIr0sEKOY1VNTjXAS")

    print(f"Triggering mock audit in Room: {room_id}...")
    
    # Reset dashboard first
    reset_req = urllib.request.Request(
        "http://localhost:3000/reset",
        method="POST"
    )
    try:
        with urllib.request.urlopen(reset_req) as response:
            print("Dashboard reset response status:", response.status)
    except Exception as e:
        print("Reset failed:", e)

    # Prepare message payload
    message = f"@rogiebacanto2002/planner-agent Please audit the following contract for compliance against GDPR, CCPA/CPRA, HIPAA, SOC 2, SOX, AML/KYC.\n\nCONTRACT NAME: sample_contract\n\nCONTRACT TEXT:\n{contract_text}"
    payload = {
        "content": message,
        "mentions": ["@rogiebacanto2002/planner-agent"]
    }

    req = urllib.request.Request(
        f"http://localhost:3000/send-message?room_id={room_id}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            print("Successfully sent message to proxy. Response:")
            print(json.dumps(result, indent=2))
    except Exception as e:
        print("Error sending message to proxy:", e)

if __name__ == "__main__":
    main()
