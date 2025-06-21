#!/usr/bin/env python3
"""
Helper script to create a .env file for the Factify project.
This script will create a .env file with all necessary environment variables.
"""

import os

def create_env_file():
    """Creates a .env file with the necessary environment variables."""
    
    env_content = """# Factify Environment Variables
# Add your actual values below

# --- API Keys ---
GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"

# --- LLM Configuration ---
# Available models: gemini-1.5-flash, gemini-1.5-pro, gemini-pro
GEMINI_MODEL="gemini-1.5-flash"
LLM_TEMPERATURE="0.3"
LLM_MAX_TOKENS="1024"

# --- Caching Configuration ---
CACHE_ENABLED="true"
CACHE_EXPIRATION_TIME_SECONDS="3600"
"""

    # Check if .env already exists
    if os.path.exists('.env'):
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("❌ Aborted. .env file not modified.")
            return False
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created successfully!")
        print("\n📝 Next steps:")
        print("1. Open the .env file")
        print("2. Replace 'YOUR_GEMINI_API_KEY_HERE' with your actual Gemini API key")
        print("3. Optionally adjust other settings like GEMINI_MODEL if needed")
        print("\n🔧 Available Gemini models:")
        print("   - gemini-1.5-flash (fast, cost-effective)")
        print("   - gemini-1.5-pro (more capable, higher cost)")
        print("   - gemini-pro (legacy model)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def show_current_config():
    """Shows the current configuration from environment variables."""
    print("\n🔍 Current configuration (from environment or defaults):")
    
    # Import settings to see current values
    try:
        from config.settings import (
            GEMINI_API_KEY, LLM_MODEL, LLM_TEMPERATURE, 
            LLM_MAX_TOKENS, CACHE_ENABLED, CACHE_EXPIRATION_TIME_SECONDS
        )
        
        print(f"   GEMINI_API_KEY: {'✅ Set' if GEMINI_API_KEY and GEMINI_API_KEY != 'YOUR_GEMINI_API_KEY_HERE' else '❌ Not set'}")
        print(f"   GEMINI_MODEL: {LLM_MODEL}")
        print(f"   LLM_TEMPERATURE: {LLM_TEMPERATURE}")
        print(f"   LLM_MAX_TOKENS: {LLM_MAX_TOKENS}")
        print(f"   CACHE_ENABLED: {CACHE_ENABLED}")
        print(f"   CACHE_EXPIRATION_TIME_SECONDS: {CACHE_EXPIRATION_TIME_SECONDS}")
        
    except Exception as e:
        print(f"❌ Error reading current config: {e}")

if __name__ == "__main__":
    print("🔧 Factify Environment Setup")
    print("=" * 40)
    
    # Show current config if settings can be loaded
    try:
        show_current_config()
    except:
        print("📝 No existing configuration found.")
    
    print("\n")
    create_env_file()
    
    # Try to show config after creation
    if os.path.exists('.env'):
        print("\n" + "=" * 40)
        try:
            show_current_config()
        except:
            print("⚠️  Please restart the application to load new environment variables.") 