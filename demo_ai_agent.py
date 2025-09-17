#!/usr/bin/env python3
"""
AI Agent Demo - Simple demonstration of AI-powered text processing
"""

import os
import sys
import time

def demo_text_operations():
    """Demonstrate text operations without needing OpenAI API key first"""
    try:
        import uno
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
            return
        
        print("✓ Connected to LibreOffice Writer!")
        
        # Get text object
        text = doc.getText()
        
        # Demonstrate text insertion
        cursor = text.createTextCursor()
        cursor.gotoEnd(False)
        
        demo_text = """
AI Writing Assistant Demo
========================

This text was inserted by the Python AI agent!

Try selecting some text and imagine you could:
- Ask AI to "rewrite this in simpler words"  
- Request "make this more professional"
- Get "expand this with examples"
- Ask for "fix grammar and spelling"

Sample text to try with:
"The utilization of artificial intelligence in document processing facilitates enhanced productivity."

Instructions:
1. Select the sample text above
2. In a real implementation, you'd use the sidebar panel
3. The AI would rewrite/improve the selected text

Current Features Working:
✓ Python ↔ LibreOffice connection
✓ Text insertion and manipulation
✓ Document access via UNO API
✓ OpenAI libraries installed

Next: Add your OpenAI API key to enable AI features!
"""
        
        cursor.setString(demo_text)
        print("✓ Demo text inserted into document!")
        
        # Show current document stats
        word_count = len(doc.getText().getString().split())
        print(f"✓ Document now has approximately {word_count} words")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ai_capability():
    """Test if AI features are ready"""
    try:
        import openai
        
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key.startswith('sk-'):
            print("✓ OpenAI API key found - AI features ready!")
            return True
        else:
            print("⚠ Set OPENAI_API_KEY environment variable to enable AI features")
            print("Example: set OPENAI_API_KEY=sk-your-api-key-here")
            return False
            
    except ImportError:
        print("❌ OpenAI library not available")
        return False

def main():
    print("LibreOffice Writer AI Agent - Demo")
    print("=" * 40)
    
    # Test basic functionality
    if demo_text_operations():
        print("\n" + "=" * 40)
        print("✅ Basic functionality working!")
        
        # Test AI readiness
        print("\nChecking AI capabilities...")
        test_ai_capability()
        
        print("\n📝 Check your LibreOffice Writer window!")
        print("You should see demo text with instructions.")
        
    else:
        print("\n❌ Connection failed. Make sure LibreOffice Writer is open.")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()