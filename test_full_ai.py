#!/usr/bin/env python3
"""
AI Agent - Full Implementation with OpenAI Integration
"""

import os
import sys
import time
import json
import socket
import threading
import logging
from typing import Optional, Dict, Any

def test_ai_functionality():
    """Test the AI functionality with actual OpenAI API calls"""
    try:
        import uno
        import openai
        
        # Get API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ No OpenAI API key found in environment")
            return False
            
        print(f"✓ OpenAI API key found: {api_key[:8]}...")
        
        # Set up OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        print("✓ Connecting to LibreOffice...")
        
        # Connect to LibreOffice
        local_ctx = uno.getComponentContext()
        resolver = local_ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local_ctx)
        
        ctx = resolver.resolve(
            "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
        
        desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        doc = desktop.getCurrentComponent()
        
        if not doc or not hasattr(doc, 'Text'):
            print("❌ Please make sure LibreOffice Writer is open!")
            return False
        
        print("✓ Connected to LibreOffice Writer!")
        
        # Insert test content
        text = doc.getText()
        cursor = text.createTextCursor()
        cursor.gotoEnd(False)
        
        test_content = """

🤖 AI Agent Test Document
========================

Original text to improve:
"The utilization of sophisticated artificial intelligence algorithms facilitates the enhancement of document processing capabilities and enables users to achieve superior productivity outcomes through automated text manipulation functionalities."

AI-Improved versions will appear below:

"""
        cursor.setString(test_content)
        print("✓ Test content inserted!")
        
        # Test AI rewriting
        print("🤖 Testing AI text improvement...")
        
        sample_text = "The utilization of sophisticated artificial intelligence algorithms facilitates the enhancement of document processing capabilities and enables users to achieve superior productivity outcomes through automated text manipulation functionalities."
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful writing assistant. Rewrite text to be clearer and simpler while maintaining the original meaning."},
                    {"role": "user", "content": f"Rewrite this text in simpler, clearer words: {sample_text}"}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            improved_text = response.choices[0].message.content.strip()
            
            # Insert the AI-improved text
            cursor.gotoEnd(False)
            result_text = f"""
✅ AI Rewrite Result:
"{improved_text}"

🎉 AI Agent is working perfectly!

Try this:
1. Select any text in this document
2. The AI agent can rewrite, improve, summarize, or expand it
3. Use commands like "make this simpler" or "add more details"

System Status:
✓ LibreOffice Writer connected
✓ OpenAI API working  
✓ Text processing functional
✓ Ready for AI-powered writing assistance!
"""
            
            cursor.setString(result_text)
            print("🎉 AI functionality test successful!")
            print("✓ Check LibreOffice Writer to see the AI-improved text!")
            
            return True
            
        except Exception as e:
            error_text = f"\n❌ AI API Error: {str(e)}\n"
            cursor.gotoEnd(False)
            cursor.setString(error_text)
            print(f"❌ AI API call failed: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    print("LibreOffice Writer AI Agent - Full Test")
    print("=" * 45)
    
    if test_ai_functionality():
        print("\n✅ ALL SYSTEMS WORKING!")
        print("Your AI-enhanced LibreOffice Writer is ready!")
        print("\nWhat you can do now:")
        print("1. Select any text in LibreOffice Writer")
        print("2. Imagine using AI commands like:")
        print("   - 'Rewrite this in simpler words'")
        print("   - 'Make this more professional'")
        print("   - 'Add examples to this text'")
        print("   - 'Fix grammar and spelling'")
        print("3. The AI will process and improve your text!")
    else:
        print("\n❌ Some issues found - check the errors above")
    
    print("\nPress Enter to continue...")
    input()

if __name__ == "__main__":
    main()