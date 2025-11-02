#!/usr/bin/env python3
"""
VPants System Runner
"""
import subprocess
import sys
import os

def main():
    # Initialize database first
    from config.database import init_database
    init_database()
    print("✅ Database initialized successfully!")
    
    # Run Streamlit app
    print("🚀 Starting VPants Streamlit App...")
    print("📱 Open http://localhost:8501 in your browser")
    os.system("streamlit run app.py")

if __name__ == "__main__":
    main()
