# Streamlit Configuration

## For Local Development
- Use `.env` file in the root directory for environment variables
- The `config.toml` contains app configuration

## For Streamlit Community Cloud Deployment
- DO NOT commit `secrets.toml` with real API keys
- Add secrets directly in the Streamlit Cloud dashboard:
  1. Go to your app settings
  2. Click on "Secrets" in the left sidebar
  3. Copy contents from `secrets.toml.example` and add your real keys

## Note
Users can provide their own OpenAI API key directly in the app sidebar, so setting OPENAI_API_KEY in secrets is optional.