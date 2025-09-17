#!/usr/bin/env python3
"""
LibreOffice Writer AI Agent Backend
Provides AI-powered text processing capabilities for LibreOffice Writer
"""

import os
import sys
import time
import json
import socket
import threading
import logging
from typing import Optional, Dict, Any

try:
    import openai
except ImportError:
    print("OpenAI package not found. Install with: pip install openai")
    sys.exit(1)

try:
    import uno
    from com.sun.star.awt import XWindowListener
    from com.sun.star.beans import XPropertyChangeListener
    from com.sun.star.text import XTextRange
    from com.sun.star.lang import XServiceInfo
    from com.sun.star.uno import XInterface
except ImportError:
    print("UNO libraries not found. Make sure LibreOffice SDK is properly installed.")
    sys.exit(1)


class AIAgentService:
    """Main AI Agent service that handles communication with LibreOffice Writer"""
    
    def __init__(self, openai_api_key: str = None, port: int = 8765):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it directly.")
        
        # Initialize OpenAI client
        openai.api_key = self.openai_api_key
        
        self.port = port
        self.running = False
        self.socket_server = None
        self.uno_context = None
        self.desktop = None
        self.current_doc = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Connect to LibreOffice
        self._connect_to_libreoffice()
    
    def _connect_to_libreoffice(self):
        """Connect to LibreOffice via UNO bridge"""
        try:
            # Connect to LibreOffice
            local_ctx = uno.getComponentContext()
            resolver = local_ctx.ServiceManager.createInstanceWithContext(
                "com.sun.star.bridge.UnoUrlResolver", local_ctx)
            
            # Try to connect to existing LibreOffice instance
            try:
                self.uno_context = resolver.resolve(
                    "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
                self.logger.info("Connected to existing LibreOffice instance")
            except:
                self.logger.warning("Could not connect to LibreOffice on port 2002. Make sure LibreOffice is running with: soffice --writer --accept='socket,host=localhost,port=2002;urp;StarOffice.ServiceManager' --nologo --nodefault --nolockcheck --norestore")
                return
            
            self.desktop = self.uno_context.ServiceManager.createInstanceWithContext(
                "com.sun.star.frame.Desktop", self.uno_context)
            
        except Exception as e:
            self.logger.error(f"Failed to connect to LibreOffice: {e}")
    
    def get_current_document(self):
        """Get the currently active Writer document"""
        if not self.desktop:
            return None
        
        try:
            doc = self.desktop.getCurrentComponent()
            if doc and hasattr(doc, 'Text'):  # Check if it's a Writer document
                self.current_doc = doc
                return doc
        except Exception as e:
            self.logger.error(f"Failed to get current document: {e}")
        
        return None
    
    def get_selected_text(self) -> Optional[str]:
        """Get currently selected text from the document"""
        doc = self.get_current_document()
        if not doc:
            return None
        
        try:
            controller = doc.getCurrentController()
            selection = controller.getSelection()
            
            if selection.getCount() > 0:
                text_range = selection.getByIndex(0)
                return text_range.getString()
        except Exception as e:
            self.logger.error(f"Failed to get selected text: {e}")
        
        return None
    
    def replace_selected_text(self, new_text: str) -> bool:
        """Replace currently selected text with new text"""
        doc = self.get_current_document()
        if not doc:
            return False
        
        try:
            controller = doc.getCurrentController()
            selection = controller.getSelection()
            
            if selection.getCount() > 0:
                text_range = selection.getByIndex(0)
                text_range.setString(new_text)
                return True
        except Exception as e:
            self.logger.error(f"Failed to replace selected text: {e}")
        
        return False
    
    def insert_text_at_cursor(self, text: str) -> bool:
        """Insert text at current cursor position"""
        doc = self.get_current_document()
        if not doc:
            return False
        
        try:
            controller = doc.getCurrentController()
            cursor = controller.getViewCursor()
            cursor.setString(text)
            return True
        except Exception as e:
            self.logger.error(f"Failed to insert text: {e}")
        
        return False
    
    def get_document_text(self) -> Optional[str]:
        """Get all text from the current document"""
        doc = self.get_current_document()
        if not doc:
            return None
        
        try:
            text = doc.getText()
            return text.getString()
        except Exception as e:
            self.logger.error(f"Failed to get document text: {e}")
        
        return None
    
    async def call_openai_api(self, prompt: str, context: str = "", max_tokens: int = 1000) -> Optional[str]:
        """Call OpenAI API with the given prompt"""
        try:
            full_prompt = f"{context}\n\nUser request: {prompt}" if context else prompt
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # or "gpt-4" if available
                messages=[
                    {"role": "system", "content": "You are an AI writing assistant integrated into LibreOffice Writer. Help users improve their documents by rewriting, editing, and enhancing text. Provide clear, concise responses."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {e}")
            return None
    
    def process_user_command(self, command: str) -> Dict[str, Any]:
        """Process a user command and return the result"""
        command = command.lower().strip()
        
        if "rewrite" in command or "improve" in command:
            return self._handle_rewrite_command(command)
        elif "summarize" in command:
            return self._handle_summarize_command(command)
        elif "expand" in command or "elaborate" in command:
            return self._handle_expand_command(command)
        elif "correct" in command or "fix" in command:
            return self._handle_correct_command(command)
        else:
            return self._handle_general_command(command)
    
    def _handle_rewrite_command(self, command: str) -> Dict[str, Any]:
        """Handle rewrite/improve commands"""
        selected_text = self.get_selected_text()
        
        if not selected_text:
            return {
                "status": "error",
                "message": "Please select text to rewrite"
            }
        
        # Extract specific instructions from command
        if "simpler" in command or "simple" in command:
            prompt = f"Rewrite this text in simpler words: {selected_text}"
        elif "formal" in command:
            prompt = f"Rewrite this text in a more formal tone: {selected_text}"
        elif "casual" in command:
            prompt = f"Rewrite this text in a more casual tone: {selected_text}"
        else:
            prompt = f"Improve and rewrite this text: {selected_text}"
        
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.call_openai_api(prompt))
            loop.close()
            
            if result:
                self.replace_selected_text(result)
                return {
                    "status": "success",
                    "message": "Text rewritten successfully",
                    "original": selected_text,
                    "result": result
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to get AI response"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing command: {str(e)}"
            }
    
    def _handle_summarize_command(self, command: str) -> Dict[str, Any]:
        """Handle summarization commands"""
        selected_text = self.get_selected_text()
        
        if not selected_text:
            # If no selection, try to summarize the whole document
            selected_text = self.get_document_text()
            if not selected_text:
                return {
                    "status": "error",
                    "message": "No text to summarize"
                }
        
        prompt = f"Summarize this text concisely: {selected_text}"
        
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.call_openai_api(prompt))
            loop.close()
            
            if result:
                # Insert summary at cursor position
                self.insert_text_at_cursor(f"\n\nSummary: {result}\n\n")
                return {
                    "status": "success",
                    "message": "Summary added to document",
                    "result": result
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to generate summary"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing command: {str(e)}"
            }
    
    def _handle_expand_command(self, command: str) -> Dict[str, Any]:
        """Handle expand/elaborate commands"""
        selected_text = self.get_selected_text()
        
        if not selected_text:
            return {
                "status": "error",
                "message": "Please select text to expand"
            }
        
        prompt = f"Expand and elaborate on this text with more details: {selected_text}"
        
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.call_openai_api(prompt, max_tokens=1500))
            loop.close()
            
            if result:
                self.replace_selected_text(result)
                return {
                    "status": "success",
                    "message": "Text expanded successfully",
                    "result": result
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to expand text"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing command: {str(e)}"
            }
    
    def _handle_correct_command(self, command: str) -> Dict[str, Any]:
        """Handle grammar/spelling correction commands"""
        selected_text = self.get_selected_text()
        
        if not selected_text:
            return {
                "status": "error",
                "message": "Please select text to correct"
            }
        
        prompt = f"Correct any grammar, spelling, and punctuation errors in this text: {selected_text}"
        
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.call_openai_api(prompt))
            loop.close()
            
            if result:
                self.replace_selected_text(result)
                return {
                    "status": "success",
                    "message": "Text corrected successfully",
                    "result": result
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to correct text"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing command: {str(e)}"
            }
    
    def _handle_general_command(self, command: str) -> Dict[str, Any]:
        """Handle general AI commands"""
        context = self.get_selected_text() or ""
        
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.call_openai_api(command, context))
            loop.close()
            
            if result:
                if context:
                    # If there was selected text, replace it
                    self.replace_selected_text(result)
                else:
                    # Otherwise, insert at cursor
                    self.insert_text_at_cursor(result)
                
                return {
                    "status": "success",
                    "message": "Command processed successfully",
                    "result": result
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to process command"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing command: {str(e)}"
            }
    
    def start_socket_server(self):
        """Start socket server for external communication"""
        self.running = True
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket_server.bind(('localhost', self.port))
            self.socket_server.listen(5)
            self.logger.info(f"AI Agent server listening on port {self.port}")
            
            while self.running:
                try:
                    client_socket, address = self.socket_server.accept()
                    self.logger.info(f"Client connected from {address}")
                    
                    # Handle client in separate thread
                    thread = threading.Thread(target=self._handle_client, args=(client_socket,))
                    thread.daemon = True
                    thread.start()
                    
                except socket.error:
                    if self.running:
                        self.logger.error("Socket error occurred")
                    break
                    
        except Exception as e:
            self.logger.error(f"Server error: {e}")
        finally:
            if self.socket_server:
                self.socket_server.close()
    
    def _handle_client(self, client_socket):
        """Handle client connection"""
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                try:
                    request = json.loads(data.decode('utf-8'))
                    command = request.get('command', '')
                    
                    result = self.process_user_command(command)
                    
                    response = json.dumps(result)
                    client_socket.send(response.encode('utf-8'))
                    
                except json.JSONDecodeError:
                    error_response = json.dumps({
                        "status": "error",
                        "message": "Invalid JSON request"
                    })
                    client_socket.send(error_response.encode('utf-8'))
                    
        except Exception as e:
            self.logger.error(f"Client handling error: {e}")
        finally:
            client_socket.close()
    
    def stop(self):
        """Stop the AI agent service"""
        self.running = False
        if self.socket_server:
            self.socket_server.close()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LibreOffice Writer AI Agent")
    parser.add_argument('--api-key', help='OpenAI API key')
    parser.add_argument('--port', type=int, default=8765, help='Socket server port (default: 8765)')
    
    args = parser.parse_args()
    
    try:
        agent = AIAgentService(openai_api_key=args.api_key, port=args.port)
        
        print("Starting LibreOffice Writer AI Agent...")
        print("Make sure LibreOffice Writer is running with:")
        print("soffice --writer --accept='socket,host=localhost,port=2002;urp;StarOffice.ServiceManager' --nologo --nodefault --nolockcheck --norestore")
        print(f"AI Agent listening on port {args.port}")
        
        agent.start_socket_server()
        
    except KeyboardInterrupt:
        print("\nShutting down AI Agent...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'agent' in locals():
            agent.stop()


if __name__ == "__main__":
    main()