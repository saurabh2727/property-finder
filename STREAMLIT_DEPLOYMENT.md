# Streamlit Community Cloud Deployment Guide

## ✅ Pre-deployment Checklist

Your app is now ready for Streamlit Community Cloud deployment:
- ✅ Code pushed to GitHub: `saurabh2727/property-finder`
- ✅ requirements.txt configured
- ✅ .streamlit/config.toml configured
- ✅ User API key input added (no server-side secrets required)
- ✅ .gitignore updated to exclude sensitive files

## 🚀 Deployment Steps

### Step 1: Sign up for Streamlit Community Cloud
1. Go to https://streamlit.io/cloud
2. Click "Sign up" and authenticate with GitHub
3. Grant Streamlit access to your repositories

### Step 2: Deploy Your App
1. Click "New app" button
2. Select the following:
   - **Repository:** `saurabh2727/property-finder`
   - **Branch:** `main`
   - **Main file path:** `app.py`
3. Click "Deploy!"

### Step 3: Configure App Settings (Optional)

#### Custom Subdomain
1. Once deployed, click the ⋮ menu → "Settings"
2. Go to "General" tab
3. Change subdomain to something like: `property-insight.streamlit.app`

#### Secrets (Optional - Not Required)
Since users provide their own API keys in the app, you don't need to configure secrets. But if you want a fallback API key:

1. Click "Settings" → "Secrets"
2. Add (optional):
```toml
OPENAI_API_KEY = "your-fallback-api-key-here"
```

### Step 4: Access Your App
Your app will be available at:
- Default URL: `https://[your-app-name].streamlit.app`
- Custom subdomain: `https://property-insight.streamlit.app` (if configured)

## 🔐 Security Notes

### For Users
- Users enter their own OpenAI API key in the sidebar
- API keys are stored in session state only (not persisted)
- Keys are lost when session ends (intentional for security)

### For Deployment
- Never commit actual API keys to GitHub
- The `.env` file is excluded from git
- Secrets.toml is excluded from git
- App works without server-side secrets

## 🎯 User Instructions

Once deployed, users should:
1. Open the app
2. Enter their OpenAI API key in the sidebar (get from: https://platform.openai.com/api-keys)
3. Upload customer requirements document
4. Import suburb data CSV
5. Generate recommendations

## 📊 Usage Limits

Streamlit Community Cloud (Free Tier):
- ✅ 1 GB RAM per app
- ✅ 1 CPU core
- ✅ Unlimited apps
- ⚠️ Apps sleep after inactivity (wake on visit)
- ⚠️ Public by default (can add password protection)

## 🛠️ Post-Deployment

### Monitor Your App
- Check logs in Streamlit Cloud dashboard
- Monitor app performance
- Watch for errors in the logs tab

### Update Your App
To update after deployment:
```bash
git add .
git commit -m "Update message"
git push origin main
```
Streamlit Cloud will auto-deploy the changes.

### Rollback (if needed)
1. Go to app settings
2. Click "Manage app"
3. Select previous commit to deploy

## 🐛 Common Issues

### Issue: App won't start
**Solution:** Check logs in Streamlit dashboard for import errors

### Issue: Dependency conflicts
**Solution:** Ensure requirements.txt versions are compatible

### Issue: API key not working
**Solution:** Users should check their API key is valid and has credits

### Issue: App is slow
**Solution:**
- Optimize data loading
- Use @st.cache_data decorators
- Reduce dataset size

## 🎉 Next Steps

After successful deployment:
1. ✅ Test all features in production
2. ✅ Share URL with users
3. ✅ Collect feedback
4. ✅ Monitor usage and errors
5. ✅ Update documentation

## 📞 Support

- Streamlit Docs: https://docs.streamlit.io
- Community Forum: https://discuss.streamlit.io
- GitHub Issues: https://github.com/saurabh2727/property-finder/issues

---

**Your Repository:** https://github.com/saurabh2727/property-finder
**Streamlit Cloud:** https://streamlit.io/cloud