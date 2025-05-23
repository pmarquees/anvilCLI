#!/usr/bin/env python3
"""
Demo showing how to configure v0 API key with anvil.
"""

import os
from pathlib import Path

def demo_configuration():
    """Show different ways to configure the v0 API key."""
    print("🔧 Anvil v0 API Key Configuration Demo")
    print("=" * 50)
    
    print("\n1️⃣ GLOBAL CONFIGURATION (Recommended)")
    print("   Sets API key for all projects on your machine")
    print("   Command: anvil sketch config --set-key YOUR_KEY --global")
    print(f"   Location: {Path.home() / '.anvil' / '.env'}")
    
    print("\n2️⃣ PROJECT CONFIGURATION")
    print("   Sets API key for current project only")
    print("   Command: anvil sketch config --set-key YOUR_KEY")
    print(f"   Location: {Path.cwd() / '.env'}")
    print("   💡 Don't forget to add .env to .gitignore!")
    
    print("\n3️⃣ MANUAL .ENV FILE")
    print("   Create .env file manually:")
    print("   echo 'V0_API_KEY=your_key_here' > .env")
    
    print("\n4️⃣ ENVIRONMENT VARIABLE (Temporary)")
    print("   For current session only:")
    print("   export V0_API_KEY=your_key_here")
    
    print("\n🔍 CHECK CONFIGURATION")
    print("   Command: anvil sketch config --show")
    print("   Shows where your key is loaded from")
    
    print("\n🔄 PRIORITY ORDER")
    print("   Anvil checks for API key in this order:")
    print("   1. Current directory .env file")
    print("   2. Global ~/.anvil/.env file")
    print("   3. Environment variable V0_API_KEY")
    
    print("\n✨ QUICK START")
    print("   1. Get your API key from https://v0.dev")
    print("   2. Run: anvil sketch config --set-key YOUR_KEY --global")
    print("   3. Start sketching: anvil sketch create 'your prompt'")

if __name__ == "__main__":
    demo_configuration() 