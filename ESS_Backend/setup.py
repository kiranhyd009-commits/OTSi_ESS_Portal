#!/usr/bin/env python3
"""
OTSI Attendance Portal - Backend Setup Script
Helps with initial configuration and database setup
"""

import os
import sys
import subprocess
import getpass
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def print_step(step, text):
    """Print a formatted step"""
    print(f"[{step}] {text}")


def check_python():
    """Check Python version"""
    print_step("1", "Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current:", f"{version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")


def create_venv():
    """Create virtual environment"""
    print_step("2", "Creating virtual environment...")
    
    if os.path.exists('venv'):
        print("ℹ️  Virtual environment already exists")
        return
    
    try:
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Virtual environment created")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def activate_venv():
    """Get activation command"""
    if os.name == 'nt':  # Windows
        return 'venv\\Scripts\\activate'
    else:  # Unix
        return 'source venv/bin/activate'


def install_dependencies():
    """Install Python dependencies"""
    print_step("3", "Installing dependencies...")
    
    try:
        pip = 'venv\\Scripts\\pip' if os.name == 'nt' else 'venv/bin/pip'
        subprocess.run([pip, 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def setup_env_file():
    """Setup .env file"""
    print_step("4", "Setting up environment variables...")
    
    env_path = Path('.env')
    
    if env_path.exists():
        print("ℹ️  .env file already exists")
        overwrite = input("Overwrite? (y/n): ").lower() == 'y'
        if not overwrite:
            return
    
    print("\n📝 Enter your Supabase credentials:")
    supabase_url = input("Supabase URL (https://...supabase.co): ").strip()
    supabase_key = input("Supabase API Key: ").strip()
    jwt_secret = getpass.getpass("JWT Secret Key (leave blank to generate): ").strip()
    
    if not jwt_secret:
        import secrets
        jwt_secret = secrets.token_urlsafe(32)
        print(f"Generated JWT Secret: {jwt_secret}")
    
    env_content = f"""# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_APP=app.py

# JWT Configuration
JWT_SECRET_KEY={jwt_secret}

# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_KEY={supabase_key}

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5000,http://127.0.0.1:5000

# Server Configuration
SERVER_PORT=5000
SERVER_HOST=0.0.0.0
"""
    
    env_path.write_text(env_content)
    print("✅ .env file created")


def test_connection():
    """Test database connection"""
    print_step("5", "Testing Supabase connection...")
    
    try:
        from database import SupabaseDB
        client = SupabaseDB.get_client()
        print("✅ Supabase connection successful")
        return True
    except Exception as e:
        print(f"⚠️  Connection test failed: {e}")
        print("   Make sure Supabase credentials in .env are correct")
        return False


def display_next_steps():
    """Display next steps"""
    print_header("Setup Complete! 🎉")
    
    print("Next steps:\n")
    print("1. Setup Supabase Database:")
    print("   - Go to https://supabase.com")
    print("   - Create a new project")
    print("   - Copy Project URL and API Key to .env")
    print("   - Run database schema:\n")
    print("     a) Go to Supabase SQL Editor")
    print("     b) Create a new query")
    print("     c) Copy content from database_schema.sql")
    print("     d) Execute the query\n")
    
    print("2. Activate virtual environment:")
    print(f"   {activate_venv()}\n")
    
    print("3. Run the application:")
    print("   python app.py\n")
    
    print("4. API will be available at:")
    print("   http://localhost:5000\n")
    
    print("5. Check API status:")
    print("   curl http://localhost:5000/api/health\n")
    
    print("📚 For more information, see README.md")


def main():
    """Main setup function"""
    print_header("OTSI Attendance Portal - Backend Setup")
    
    check_python()
    create_venv()
    install_dependencies()
    setup_env_file()
    
    connection_ok = test_connection()
    
    display_next_steps()
    
    if not connection_ok:
        print("\n⚠️  Please verify your Supabase credentials before running the app")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
