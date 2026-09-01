# Personal Assistant with Strands Agents

This sample implements a personal assistant agent using Strands' [agents as tools](https://strandsagents.com/latest/user-guide/concepts/multi-agent/agents-as-tools/) functionality.


## 🏗️ Architecture Overview
![architecture](images/multi-agent-architecture.png)

## 🌟 Agent tools

### 📅 Calendar Assistant
- **Create Appointments**: Schedule new appointments with date, time, location, and descriptions
- **List All Appointments**: View all scheduled appointments in a formatted list
- **Update Appointments**: Modify existing appointments by ID
- **Daily Agenda**: Get a formatted agenda for any specific date
- **Time Awareness**: Built-in current time functionality

### 💻 Coding Assistant  
- **Editor**: Editor tool designed to do changes iteratively on multiple files.
- **Journal**: Daily journal management tool for Strands Agent.
- **Python REPL** & **Shell** *(Unix / WSL only)*: Run code and shell commands. These `strands_tools` need a Unix pseudo-terminal (`fcntl`/`pty`) and are **omitted on native Windows** — see the note in `code_assistant.py`. Add them back on WSL / Linux / macOS.

### 🔍 Search Agent
- **Web Search**: Powered by [OpenRouter](https://openrouter.ai/) using a web-search-capable model (`perplexity/sonar`) — real-time information, no Docker required

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- [AWS CLI](https://awscli.amazonaws.com/AWSCLIV2.msi) (install via `winget install Amazon.AWSCLI`)
- AWS Account with Bedrock access (a current Claude model enabled in us-east-1, e.g. **Claude Sonnet 4.5**)
- An [OpenRouter API key](https://openrouter.ai/keys) (only for the Search Assistant)
- Required Python packages (see requirements.txt)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Azleem01/strands-ai-agent-app
```

2. **Set up a Python virtual environment** (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks the script with "running scripts is disabled on this system", run the following once, then re-run the activate command above:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

3. **Install dependencies**:
```powershell
pip install -r requirements.txt
```

> This installs everything the agents need, including `python-dotenv` (used by the Search Assistant) and the `openai` client (used to talk to OpenRouter).

4. **Install the AWS CLI** (needed for `aws configure`):
```powershell
winget install Amazon.AWSCLI
```
If `winget` isn't available, download the installer instead: https://awscli.amazonaws.com/AWSCLIV2.msi

> **Important:** After installing, the `aws` command won't be recognized in your **current** PowerShell window — its PATH was set when the window opened. Either open a **new** PowerShell window (and re-run `.venv\Scripts\Activate.ps1`), or refresh the PATH in the current session:
> ```powershell
> $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
> ```
> Confirm it works with `aws --version`.

5. **Configure AWS credentials** (PowerShell):
```powershell
aws configure
```
Enter your Access Key, Secret Key, region (`us-east-1`), and output format (`json`). This persists to `%USERPROFILE%\.aws\`.

Or, to skip the CLI entirely, set them as environment variables for the current session (these last only until the window is closed):
```powershell
$env:AWS_ACCESS_KEY_ID="your_access_key"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key"
$env:AWS_DEFAULT_REGION="us-east-1"
```

> **Bedrock model access:** In the [AWS Bedrock console](https://console.aws.amazon.com/bedrock/) → **Model access**, enable a current Claude model (e.g. **Claude Sonnet 4.5**) in **us-east-1**. Without it the agents fail with an access/validation error even when credentials are valid.

6. **Set up OpenRouter API** (only needed for the Search Assistant):

Get a key at https://openrouter.ai/keys, then create a `.env` file in the project root (copy `.env.example`) containing:
```
OPENROUTER_API_KEY=your_openrouter_api_key
```
`search_assistant.py` loads this automatically via `python-dotenv`. Alternatively, set it for the current session (PowerShell):
```powershell
$env:OPENROUTER_API_KEY="your_openrouter_api_key"
```
The Search Assistant uses OpenRouter's `perplexity/sonar` model for native web search — **no Docker required**. Edit `model_id` in `search_assistant.py` to use a different OpenRouter model.

### Choosing / changing the model

Each agent sets its model near the top of its `.py` file:
```python
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
)
```
Model IDs get **retired over time** — an old ID fails with a "legacy" or "not available for this account" error. To see what's currently available to your account and region:
```powershell
aws bedrock list-inference-profiles --region us-east-1 --query "inferenceProfileSummaries[?contains(inferenceProfileId,'claude')].inferenceProfileId" --output text
```
Then set the same `model_id=` in the three Bedrock agents (`calendar_assistant.py`, `code_assistant.py`, `personal_assistant.py`). Examples confirmed working at time of writing: `us.anthropic.claude-sonnet-4-5-20250929-v1:0` (balanced) and `us.anthropic.claude-haiku-4-5-20251001-v1:0` (cheapest/fastest — handy for demos on your own bill). The **Search Assistant** runs on OpenRouter instead — change its `model_id` inside `search_assistant.py`.

### Quick Start

#### Calendar Assistant
```bash
python -u calendar_assistant.py
```

#### Coding Assistant
```bash
python -u code_assistant.py
```

#### Search Assistant
```bash
python -u search_assistant.py
```

#### Personal Assistant (multi-agent collaboration)
```bash
python -u personal_assistant.py
```

## 🛠️ Usage Examples

### Calendar Agent
```
👤 You: Schedule a dentist appointment for tomorrow at 2 PM
🤖 CalendarBot: ✅ Appointment Created Successfully!
================================
📅 Date: 2024-01-15
🕐 Time: 14:00
📍 Location: Dental Clinic
📝 Title: Dentist Appointment
🆔 ID: abc123-def456-ghi789
```

### Coding Agent
```
👨‍💻 You: Create a Python function to calculate fibonacci numbers
🤖 CodingBot: I'll create an efficient fibonacci function for you...
```

### Search Agent 
```
👨‍💻 You: What is Strands Agents?
🤖 WebSearchBot: Let me search about Strands Agents...
```

### Daily Agenda
```
👤 You: What's my agenda for today?
🤖 CalendarBot: 📅 Agenda for 2024-01-15:
==============================
1. 🕐 09:00 - Team Meeting
   📍 Location: Conference Room A
   🆔 ID: meeting123
```

## 🔧 Configuration

### Environment Variables
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1

# Search Integration (OpenRouter)
OPENROUTER_API_KEY=your_openrouter_api_key
```

## 🧯 Troubleshooting (Windows)

| Symptom | Cause | Fix |
|---|---|---|
| `source : The term 'source' is not recognized` | `source` is macOS/Linux syntax | Activate with `.venv\Scripts\Activate.ps1` |
| `Activate.ps1 cannot be loaded because running scripts is disabled` | PowerShell execution policy | Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` once, then activate again |
| `aws : The term 'aws' is not recognized` | AWS CLI was just installed; this window's PATH is stale | Open a **new** PowerShell window (and re-activate the venv), or refresh PATH per step 4 |
| `ModuleNotFoundError: No module named 'strands'` (even though it's installed) | The venv's `Scripts` folder fell off PATH (e.g. after manually rebuilding `$env:Path`) | Re-run `.venv\Scripts\Activate.ps1`, or run explicitly: `.\.venv\Scripts\python.exe -u calendar_assistant.py` |
| `AccessDeniedException ... not authorized to perform: bedrock:InvokeModel...` | The IAM user has no Bedrock permissions | Attach **AmazonBedrockFullAccess** (or an inline Bedrock policy) to the user |
| `... marked by provider as Legacy` / `... is not available for this account` | The model ID is retired, or not enabled for your account | Pick a current model (see [Choosing / changing the model](#choosing--changing-the-model)) and update the Bedrock agents |
| `ModuleNotFoundError: No module named 'fcntl'` (running `code_assistant.py`) | `python_repl`/`shell` tools are Unix-only | They're omitted on Windows (Editor + Journal remain); use WSL/Linux/macOS for the full toolset |
| `ValueError: OPENROUTER_API_KEY environment variable is required` | Search Assistant has no OpenRouter key | Add `OPENROUTER_API_KEY` to `.env` (see step 6) |

**Happy Assisting!** 🤖✨