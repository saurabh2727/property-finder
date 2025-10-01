# Streamlit Configuration

## 🔑 API Key Setup (Recommended - Eliminates Manual Entry!)

### For Streamlit Cloud Deployment (Recommended)
1. Go to your [Streamlit Cloud dashboard](https://share.streamlit.io/)
2. Click on your app → "Settings" → "Secrets"
3. Add the following:
   ```toml
   OPENAI_API_KEY = "sk-your-actual-api-key-here"
   ```
4. Click "Save" - the app will restart with the API key pre-configured

### For Local Development
1. Create `secrets.toml` in this directory:
   ```bash
   cp secrets.toml.example secrets.toml
   ```
2. Edit `secrets.toml` and add your actual API key
3. The file is in `.gitignore` so it won't be committed

## Benefits of Using Secrets

✅ **No more entering API key every session** - Key persists across all sessions
✅ **Secure** - Keys stored in Streamlit secrets, not in code
✅ **Flexible** - Users can still override with their own key if needed
✅ **Works everywhere** - Both local development and cloud deployment

## Files

- `config.toml` - Streamlit app configuration (UI, theme, etc.)
- `secrets.toml.example` - Template for API keys (DO NOT commit secrets.toml)

## Alternative: User-Provided Keys

If you don't configure `OPENAI_API_KEY` in secrets, users will be prompted to enter their own API key in the sidebar each session.