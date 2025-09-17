#!/usr/bin/env python3
"""
Interactive AI Writing Assistant for LibreOffice Writer
"""

import os
import sys
import time

def interactive_ai_session():
    """Interactive session for testing AI commands"""
    try:
        import uno
        import openai
        
        # Set up OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        client = openai.OpenAI(api_key=api_key)
        
        # Connect to LibreOffice
        local_ctx = uno.getComponentContext()
        resolver = local_ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local_ctx)
        
        ctx = resolver.resolve(
            "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
        
        desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
        doc = desktop.getCurrentComponent()
        
        if not doc or not hasattr(doc, 'Text'):
            print("❌ LibreOffice Writer not found!")
            return
        
        print("✅ Connected to LibreOffice Writer!")
        print("\n" + "="*50)
        print("🤖 AI WRITING ASSISTANT - INTERACTIVE MODE")
        print("="*50)
        print("\nInstructions:")
        print("1. Select text in LibreOffice Writer")
        print("2. Type commands here like:")
        print("   - 'rewrite in simpler words'")
        print("   - 'make more professional'")
        print("   - 'add examples'")
        print("   - 'fix grammar'")
        print("3. Press Enter and see the magic!")
        print("\nType 'quit' to exit")
        print("-" * 50)
        
        while True:
            try:
                # Get user command
                command = input("\n🤖 AI Command: ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not command:
                    continue
                
                # Get selected text from LibreOffice
                controller = doc.getCurrentController()
                selection = controller.getSelection()
                
                if selection.getCount() == 0:
                    print("⚠️  Please select some text in LibreOffice Writer first!")
                    continue
                
                selected_text = selection.getByIndex(0).getString()
                
                if not selected_text.strip():
                    print("⚠️  No text selected!")
                    continue
                
                print(f"📝 Selected text: {selected_text[:100]}{'...' if len(selected_text) > 100 else ''}")
                print("🤖 Processing with AI...")
                
                # Create AI prompt
                if "rewrite" in command.lower() or "simpler" in command.lower():
                    prompt = f"Rewrite this text to be clearer and simpler: {selected_text}"
                elif "professional" in command.lower() or "formal" in command.lower():
                    prompt = f"Rewrite this text in a more professional tone: {selected_text}"
                elif "example" in command.lower():
                    prompt = f"Expand this text by adding relevant examples: {selected_text}"
                elif "grammar" in command.lower() or "fix" in command.lower():
                    prompt = f"Fix any grammar, spelling, and punctuation errors: {selected_text}"
                elif "summary" in command.lower() or "summarize" in command.lower():
                    prompt = f"Summarize this text concisely: {selected_text}"
                else:
                    prompt = f"{command}. Text to process: {selected_text}"
                
                # Call OpenAI API
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful writing assistant. Process the user's request and improve their text accordingly. Return only the improved text without quotes or additional commentary."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                improved_text = response.choices[0].message.content.strip()
                
                # Replace selected text with improved version
                selection.getByIndex(0).setString(improved_text)
                
                print(f"✅ Text updated in LibreOffice!")
                print(f"💡 Result: {improved_text[:150]}{'...' if len(improved_text) > 150 else ''}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Setup error: {e}")

def main():
    print("Starting Interactive AI Writing Assistant...")
    interactive_ai_session()

if __name__ == "__main__":
    main()