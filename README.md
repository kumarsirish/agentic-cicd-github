# Agentic CI/CD with GitHub Actions + LangChain + Gemini

## Overview

This project runs a GitHub Actions pipeline that:
1. Installs dependencies
2. Builds Python code
3. Runs tests
4. Uses a LangChain + Gemini agent to analyze test output
5. Applies a deployment gate (`GO`, `RETRY`, `STOP`)
6. Deploys only when allowed by the gate

Pipeline definition: [.github/workflows/agentic-cicd.yml](.github/workflows/agentic-cicd.yml)

---

## Pre-step: Setup (No Installation Needed!)

Unlike Jenkins, GitHub Actions runs entirely in the cloud. You only need:

1. A **free GitHub account** — [github.com](https://github.com)
2. A **Gemini API key** — [aistudio.google.com](https://aistudio.google.com)

### Add the Secret

1. Go to your repo on GitHub
2. Click **Settings → Secrets and variables → Actions**
3. Click **New repository secret**
4. Name: `GEMINI_API_KEY`
5. Value: your Gemini API key
6. Click **Add secret**

That's it — no servers, no plugins, no configuration files!

---

## CI/CD Flow (GitHub Actions Stages)

### 1) Install Dependencies
- Installs packages from [requirements.txt](requirements.txt) via `pip install`

### 2) Build
- Compiles [app.py](app.py) using:
  - `python -m py_compile app.py`

### 3) Test
- Runs tests from [app.py](app.py) via `pytest app.py`
- Stores output in `test-results.log`

### 4) LangChain Agent Analysis
- Runs [ai_agent.py](ai_agent.py)
- Agent uses **Gemini 2.5 Flash** to read `test-results.log`
- Writes its decision to `decision.txt`

### 5) Decision Gate
- Reads `decision.txt`
- Behavior:
  - `STOP` → pipeline fails ❌
  - `RETRY` → reruns tests once 🔁
  - `GO` → continues to deploy ✅

### 6) Deploy
- Runs [deploy.sh](deploy.sh)

---

## What happens when AGENT says `RETRY` or `STOP`?

### If decision is `RETRY`
1. GitHub Actions detects `RETRY` in `decision.txt`
2. Re-runs `pytest app.py` once
3. If retry passes → pipeline continues to Deploy
4. If retry fails → pipeline fails

### If decision is `STOP`
1. GitHub Actions detects `STOP` in `decision.txt`
2. Exits with error code 1
3. Pipeline is marked **FAILURE** ❌
4. Deploy stage is skipped

---

## Triggering the Pipeline

The pipeline runs automatically on:
- Every **push** to `main`
- Every **pull request** targeting `main`

To trigger manually: push any change to `main`, or go to **Actions → Agentic CI/CD → Run workflow**.

---

## Local Run (Optional)

Create a `.env` file:
```
GEMINI_API_KEY=your_key_here
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Run tests:
```bash
pytest app.py > test-results.log || true
```

Run agent:
```bash
python ai_agent.py
```

---

## Key Changes from Jenkins Version

| Jenkins | GitHub Actions |
|---|---|
| `Jenkinsfile` | `.github/workflows/agentic-cicd.yml` |
| `credentials('OPENAI_API_KEY')` | `${{ secrets.GEMINI_API_KEY }}` |
| `ChatOpenAI` (OpenAI) | `ChatGoogleGenerativeAI` (Gemini) |
| `gpt-4o-mini` | `gemini-2.5-flash` |
| `langchain-openai` | `langchain-google-genai` |
| Requires server setup | Runs free in the cloud ☁️ |
