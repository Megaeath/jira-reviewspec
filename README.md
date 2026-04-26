# jira-reviewspec

A Python project for Jira review specifications.

## Project Structure

- `/app-log/`: Logs of AI review activities.
- `skill.md`: Operational rules and AI instructions.

## Development Rules

1. **Always read `skill.md`** before starting work.
2. **Lint and Test** before every commit/submission.
3. **Log every session** in `/app-log/`.

## Setup

1. **Create and Activate Virtual Environment**:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file and add your credentials:

   ```env
   GEMINI_API_KEY=your_gemini_api_key
   GEMINI_MODELS=["gemini-1.5-flash", "gemini-1.5-pro"]
   GEMINI_MODEL=gemini-1.5-flash
   CONFLUENCE_URL=https://your-domain.atlassian.net
   CONFLUENCE_USER=your-email@example.com
   CONFLUENCE_TOKEN=your_atlassian_api_token
   APP_USERNAME=admin
   APP_PASSWORD=password123
   APP_ENV=dev
   ```

## Running the POC

```bash
streamlit run app.py
```

## Deployment to Streamlit Cloud

1. **Push code to GitHub**:
   Ensure all changes are pushed to your repository (e.g., `https://github.com/Megaeath/jira-reviewspec.git`).

2. **Connect to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io/).
   - Click "New app".
   - Select the repository, branch, and `app.py` as the main file path.

3. **Configure Secrets**:
   In Streamlit Cloud, go to **Settings > Secrets** and add your environment variables from `.env`:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key"
   GEMINI_MODEL = "gemini-1.5-flash"
   CONFLUENCE_URL = "https://your-domain.atlassian.net"
   CONFLUENCE_USER = "your-email@example.com"
   CONFLUENCE_TOKEN = "your_atlassian_api_token"
   APP_USERNAME = "admin"
   APP_PASSWORD = "password123"
   APP_ENV = "prod"
   ```

## Project Structure

- `app.py`: Streamlit UI.
- `orchestrator.py`: LLM process logic.
- `utils.py`: Markdown parsing utilities.
- `/app-log/`: Logs of AI review activities.
- `skill.md`: Operational rules and AI instructions.
