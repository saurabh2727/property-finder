#!/usr/bin/env python3
"""
Setup script for Property Insight App
"""

import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists():
        print("🔧 Creating .env file...")

        # Copy from example if exists
        if env_example.exists():
            with open(env_example, 'r') as f:
                content = f.read()
        else:
            content = """# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Database Configuration
DATABASE_URL=sqlite:///property_insights.db

# Application Settings
APP_DEBUG=False
"""

        with open(env_file, 'w') as f:
            f.write(content)

        print("✅ .env file created!")
        print("⚠️  Please update .env file with your actual API keys")
        return False  # Return False to indicate manual setup needed
    else:
        print("✅ .env file already exists")
        return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")

    directories = [
        "data/raw",
        "data/processed",
        "logs",
        "exports"
    ]

    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {dir_path}")

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")

    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required!")
        return False

    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Property Insight App...")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Create directories
    create_directories()

    # Install requirements
    if not install_requirements():
        print("❌ Setup failed at requirements installation")
        sys.exit(1)

    # Create environment file
    env_ready = create_env_file()

    print("\n" + "=" * 50)
    print("🎉 Setup completed!")

    if not env_ready:
        print("\n⚠️  IMPORTANT: Please configure your .env file with:")
        print("   - OpenAI API key for AI features")
        print("   - Database settings (optional)")
        print("\n📋 Next steps:")
        print("   1. Edit .env file with your API keys")
        print("   2. Run: streamlit run app.py")
        print("   3. Open browser to http://localhost:8501")
    else:
        print("\n🚀 Ready to run!")
        print("   Run: streamlit run app.py")
        print("   Open browser to http://localhost:8501")

if __name__ == "__main__":
    main()