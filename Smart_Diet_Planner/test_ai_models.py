#!/usr/bin/env python
"""
Test script to check available Google AI models
"""
import os
import sys
import django

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FitBuddy.settings')
django.setup()

import google.generativeai as genai
from django.conf import settings

def test_available_models():
    """Test what Google AI models are available"""
    try:
        api_key = getattr(settings, 'GOOGLE_API_KEY', '')
        if not api_key:
            print("❌ No API key found")
            return
            
        print(f"✅ API key found: {api_key[:10]}...")
        genai.configure(api_key=api_key)
        
        print("\n=== Available Models ===")
        models = genai.list_models()
        
        for model in models:
            print(f"Model: {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Description: {model.description}")
            print(f"  Supported Methods: {model.supported_generation_methods}")
            print()
            
    except Exception as e:
        print(f"❌ Error listing models: {e}")

if __name__ == "__main__":
    test_available_models()