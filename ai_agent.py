from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os


@tool
def read_logs(log_path: str) -> str:
    """Read CI/CD test logs from the given file path."""
    with open(log_path, "r") as f:
        return f.read()


@tool
def retry_recommendation(error_text: str) -> str:
    """Check whether retry is useful based on the error text."""
    flaky_keywords = [
        "timeout",
        "connection",
        "network"
    ]

    for word in flaky_keywords:
        if word in error_text.lower():
            return "RETRY"

    return "STOP"


load_dotenv(override=True)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GEMINI_API_KEY")
)

tools = [
    read_logs,
    retry_recommendation
]

agent = create_agent(
    model=llm,
    tools=tools
)

prompt = '''
You are a CI/CD agent.

1. Read test-results.log using the read_logs tool
2. Determine if deployment should proceed
3. Use retry_recommendation tool if you detect errors

Rules:
- Test failures → STOP
- Network/timeout issue → RETRY
- All tests passed → GO

Return only one word at the end: GO, RETRY, or STOP
'''

if __name__ == "__main__":
    if not os.path.exists("test-results.log"):
        decision = "STOP"
        with open("decision.txt", "w") as f:
            f.write(decision)
        print("Reason: test-results.log not found, so deployment is blocked.")
        print("Agent Decision:", decision)
        raise SystemExit(0)

    response = agent.invoke({
        "messages": [{"role": "user", "content": prompt}]
    })

    raw_output = response["messages"][-1].content.strip()

    decision = "STOP"
    for word in ["GO", "RETRY", "STOP"]:
        if word in raw_output.upper():
            decision = word
            break

    reason = "Agent analyzed test-results.log and selected the safest action."
    if decision == "STOP":
        reason = "Agent found test failure or non-retryable issue in test-results.log."
    elif decision == "RETRY":
        reason = "Agent detected a possible transient issue (network/timeout), so retry is recommended."
    elif decision == "GO":
        reason = "Agent found no blocking failures in test-results.log."

    with open("decision.txt", "w") as f:
        f.write(decision)

    print("Reason:", reason)
    print("Agent Decision:", decision)
