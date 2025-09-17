#!/usr/bin/env python3
"""
Simple test script to verify LibreOffice Writer AI integration
"""

import sys
import time
import os

def test_libreoffice_connection():
    """Test if we can connect to LibreOffice"""
    try:
        import uno
        print("✓ UNO library found")
        
        # Connect to LibreOffice
        local_ctx = uno.getComponentContext()
        resolver = local_ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local_ctx)
        
        print("Attempting to connect to LibreOffice...")
        try:
            ctx = resolver.resolve(
                "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
            print("✓ Connected to LibreOffice successfully!")
            
            # Get desktop
            desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
            
            # Get current document
            doc = desktop.getCurrentComponent()
            if doc and hasattr(doc, 'Text'):
                print("✓ Writer document is active!")
                
                # Try to insert some text
                text = doc.getText()
                cursor = text.createTextCursor()
                cursor.setString("Hello from AI Agent! This text was inserted by the Python script.\n\n")
                
                print("✓ Successfully inserted text into document!")
                return True
            else:
                print("⚠ No Writer document found. Please open LibreOffice Writer.")
                return False
                
        except Exception as e:
            print(f"✗ Failed to connect to LibreOffice: {e}")
            print("Make sure LibreOffice is running with UNO bridge enabled.")
            return False
            
    except ImportError:
        print("✗ UNO library not found. LibreOffice SDK may not be properly installed.")
        return False

def test_openai_setup():
    """Test OpenAI setup"""
    try:
        import openai
        print("✓ OpenAI library found")
        
        # Check for API key
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key.startswith('sk-'):
            print("✓ OpenAI API key found in environment")
            return True
        else:
            print("⚠ OpenAI API key not found in environment. Set OPENAI_API_KEY variable.")
            print("  You can still test LibreOffice connection without AI features.")
            return False
            
    except ImportError:
        print("✗ OpenAI library not found. Install with: pip install openai")
        return False

def main():
    print("LibreOffice Writer AI Agent - Connection Test")
    print("=" * 50)
    
    # Test LibreOffice connection
    print("\n1. Testing LibreOffice Connection:")
    lo_ok = test_libreoffice_connection()
    
    # Test OpenAI setup
    print("\n2. Testing OpenAI Setup:")
    openai_ok = test_openai_setup()
    
    print("\n" + "=" * 50)
    if lo_ok:
        print("✓ LibreOffice connection successful!")
        if openai_ok:
            print("✓ Ready for AI-powered writing assistance!")
        else:
            print("⚠ AI features require OpenAI API key")
    else:
        print("✗ LibreOffice connection failed")
        print("\nTroubleshooting:")
        print("1. Make sure LibreOffice Writer is open")
        print("2. Restart LibreOffice with UNO bridge:")
        print('   Start-Process "C:\\Program Files\\LibreOffice\\program\\soffice.exe" -ArgumentList "--writer", "--accept=socket,host=localhost,port=2002;urp;StarOffice.ServiceManager"')
    
    print("\nPress Enter to continue...")
    input()

if __name__ == "__main__":
    main()