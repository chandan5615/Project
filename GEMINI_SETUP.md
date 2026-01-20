# Gemini API Setup Guide (Temporary Configuration)

This project is temporarily configured to use Google Gemini API instead of Ollama. Follow these steps to set up:

## Step 1: Get Your API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

## Step 2: Set the API Key

### Option A: Environment Variable (Recommended)

**Linux/macOS:**
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

**Windows PowerShell:**
```powershell
$env:GOOGLE_API_KEY="your-api-key-here"
```

**Windows CMD:**
```cmd
set GOOGLE_API_KEY=your-api-key-here
```

### Option B: .env File

1. Create a `.env` file in the project root:
   ```
   GOOGLE_API_KEY=your-api-key-here
   ```

2. The code will automatically load it if `python-dotenv` is installed (already included in requirements)

## Step 3: Verify Setup

Run a quick test:
```bash
# Activate virtual environment first
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source venv/bin/activate     # Linux/macOS

# Test the API key
python -c "import os; print('API Key set!' if os.getenv('GOOGLE_API_KEY') else 'API Key NOT set!')"
```

## Step 4: Run Sentinel Agent

```bash
python main.py
```

## Switching Back to Ollama

To restore Ollama configuration:

1. **Edit `agents.py`:**
   - Uncomment the Ollama import: `from langchain_community.llms import OllamaLLM`
   - Comment out the Gemini import: `# from langchain_google_genai import ChatGoogleGenerativeAI`
   - Replace the `llm` initialization with:
     ```python
     llm = OllamaLLM(
         model="llama3:8b",
         base_url="http://localhost:11434",
         temperature=0.7,
     )
     ```

2. **Edit `requirements.txt`:**
   - Uncomment: `ollama>=0.1.0`
   - Comment out: `# langchain-google-genai>=1.0.0`

3. **Install Ollama:**
   ```bash
   ollama pull llama3:8b
   ```

4. **Verify Ollama is running:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

## Troubleshooting

### "GOOGLE_API_KEY environment variable is not set"
- Make sure you've set the environment variable or created a `.env` file
- Restart your terminal after setting the environment variable
- Verify with: `echo $GOOGLE_API_KEY` (Linux/macOS) or `echo $env:GOOGLE_API_KEY` (Windows PowerShell)

### API Key Invalid
- Double-check you copied the entire API key
- Ensure there are no extra spaces or quotes
- Regenerate the key if needed from Google AI Studio

### Rate Limits
- Gemini API has rate limits based on your plan
- Free tier: 60 requests per minute
- If you hit limits, consider switching back to Ollama for unlimited local usage
