# Property Insight App - Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- Git (optional)

### Installation

1. **Clone or Download the Project**
   ```bash
   git clone <repository-url>
   cd property-finder
   ```

2. **Run Setup Script**
   ```bash
   python setup.py
   ```

3. **Configure Environment**
   Edit `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

4. **Start the Application**
   ```bash
   # Option 1: Use the runner script
   ./run_app.sh

   # Option 2: Direct streamlit command
   streamlit run app.py
   ```

5. **Access the App**
   Open your browser to: http://localhost:8501

## 📦 Manual Installation

### Step 1: Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Environment Configuration
Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
DATABASE_URL=sqlite:///property_insights.db
```

### Step 4: Create Directories
```bash
mkdir -p data/{raw,processed}
mkdir -p logs
mkdir -p exports
```

### Step 5: Run Application
```bash
streamlit run app.py
```

## 🌐 Production Deployment

### Option 1: Streamlit Community Cloud

1. **Prepare Repository**
   - Ensure all files are in a Git repository
   - Add `secrets.toml` to `.streamlit/` directory:
     ```toml
     [secrets]
     OPENAI_API_KEY = "your-api-key"
     ```

2. **Deploy**
   - Visit https://streamlit.io/cloud
   - Connect your GitHub repository
   - Select main branch and `app.py` file
   - Configure secrets in the web interface

### Option 2: Heroku Deployment

1. **Prepare Files**
   Create `Procfile`:
   ```
   web: sh setup.sh && streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

   Create `setup.sh`:
   ```bash
   mkdir -p ~/.streamlit/
   echo "\
   [general]\n\
   email = \"your-email@domain.com\"\n\
   " > ~/.streamlit/credentials.toml
   echo "\
   [server]\n\
   headless = true\n\
   enableCORS = false\n\
   port = $PORT\n\
   " > ~/.streamlit/config.toml
   ```

2. **Deploy to Heroku**
   ```bash
   heroku create your-app-name
   heroku config:set OPENAI_API_KEY=your-api-key
   git push heroku main
   ```

### Option 3: Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .
   EXPOSE 8501

   HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
   ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build and Run**
   ```bash
   docker build -t property-insight-app .
   docker run -p 8501:8501 -e OPENAI_API_KEY=your-api-key property-insight-app
   ```

### Option 4: AWS EC2 Deployment

1. **Launch EC2 Instance**
   - Ubuntu 20.04 LTS
   - Open port 8501 in security groups

2. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip
   pip3 install -r requirements.txt
   ```

3. **Configure Service**
   Create systemd service file `/etc/systemd/system/property-insight.service`:
   ```ini
   [Unit]
   Description=Property Insight App
   After=network.target

   [Service]
   Type=exec
   User=ubuntu
   WorkingDirectory=/home/ubuntu/property-finder
   ExecStart=/usr/bin/python3 -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   Restart=always
   Environment=OPENAI_API_KEY=your-api-key

   [Install]
   WantedBy=multi-user.target
   ```

4. **Start Service**
   ```bash
   sudo systemctl enable property-insight
   sudo systemctl start property-insight
   ```

## 🔐 Security Configuration

### Environment Variables
Always use environment variables for sensitive data:
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Application secret key

### Production Checklist
- [ ] API keys stored as environment variables
- [ ] Debug mode disabled (`APP_DEBUG=False`)
- [ ] HTTPS enabled (use reverse proxy like Nginx)
- [ ] Regular backups configured
- [ ] Monitoring and logging setup
- [ ] Rate limiting implemented

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```
   Solution: Ensure all requirements are installed
   pip install -r requirements.txt
   ```

2. **OpenAI API Errors**
   ```
   Solution: Check API key in .env file
   Verify API key has sufficient credits
   ```

3. **Port Already in Use**
   ```bash
   # Kill process using port 8501
   lsof -ti:8501 | xargs kill -9

   # Or use different port
   streamlit run app.py --server.port 8502
   ```

4. **Permission Errors**
   ```bash
   # Fix file permissions
   chmod +x run_app.sh
   ```

### Getting Support

1. **Check Logs**
   - Application logs in `logs/` directory
   - Streamlit logs in terminal output

2. **Debug Mode**
   Set `APP_DEBUG=True` in `.env` for detailed error messages

3. **Contact**
   - Create issue in project repository
   - Check documentation for FAQ

## 📊 Performance Optimization

### Production Optimizations

1. **Caching**
   - Enable Streamlit caching for data operations
   - Implement Redis for session storage

2. **Database**
   - Use PostgreSQL instead of SQLite for production
   - Implement connection pooling

3. **Monitoring**
   - Set up application monitoring (e.g., New Relic)
   - Configure log aggregation (e.g., ELK stack)

4. **Scaling**
   - Use load balancer for multiple instances
   - Implement container orchestration (Kubernetes)

## 🔄 Updates and Maintenance

### Regular Maintenance
- Update dependencies monthly
- Monitor API usage and costs
- Backup user data and reports
- Review and update documentation

### Version Updates
```bash
git pull origin main
pip install -r requirements.txt
systemctl restart property-insight  # If using systemd
```