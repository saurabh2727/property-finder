# Streamlit Configuration

## 🔑 API Key Setup - Two Modes

### Mode 1: Shared Admin Key (Recommended for Single User/Testing)

**Use Case:** You're the only user or want to provide a shared key for all users

**Setup:**
1. **For Streamlit Cloud:**
   - Go to your [Streamlit Cloud dashboard](https://share.streamlit.io/)
   - Click on your app → "Settings" → "Secrets"
   - Add: `OPENAI_API_KEY = "sk-your-actual-api-key-here"`
   - Click "Save"

2. **For Local Development:**
   ```bash
   cd .streamlit
   cp secrets.toml.example secrets.toml
   # Edit secrets.toml and add your key
   ```

**Benefits:**
- ✅ No API key entry required for any user
- ✅ Immediate access for everyone
- ⚠️ All users share the same OpenAI usage/costs

---

### Mode 2: Per-User Keys with Browser Storage (Recommended for Multiple Users)

**Use Case:** Multiple users, each with their own OpenAI API key

**Setup:**
- **Don't configure** `OPENAI_API_KEY` in secrets
- Each user enters their own key in the sidebar
- Click "💾 Save to Browser" to cache the key in browser localStorage
- Key automatically loads on future visits!

**Benefits:**
- ✅ Each user controls their own costs
- ✅ Separate usage tracking per user
- ✅ **Browser caching** - key saved in localStorage
- ✅ **Auto-load** - key retrieves automatically on page load
- ✅ **Persistent** - works even after closing browser/tab
- 🔒 Secure - key only accessible in user's browser

---

## Files

- `config.toml` - Streamlit app configuration (UI, theme, etc.)
- `secrets.toml.example` - Template for API keys (DO NOT commit secrets.toml)
- `secrets.toml` - Your actual secrets (auto-ignored by git)

## Recommendation

| Scenario | Recommended Mode |
|----------|------------------|
| Personal use | Mode 1 (Shared Admin Key) |
| Team with shared budget | Mode 1 (Shared Admin Key) |
| Multiple users, separate billing | Mode 2 (Per-User Keys) |
| Public demo | Mode 2 (Per-User Keys) |