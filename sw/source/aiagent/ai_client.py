#!/usr/bin/env python3
"""
Simple client to test AI agent communication
"""

import json
import socket
import sys


def send_command(command: str, host: str = 'localhost', port: int = 8765):
    """Send a command to the AI agent"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        
        request = {"command": command}
        client_socket.send(json.dumps(request).encode('utf-8'))
        
        response = client_socket.recv(4096)
        result = json.loads(response.decode('utf-8'))
        
        client_socket.close()
        return result
        
    except Exception as e:
        return {"status": "error", "message": f"Connection error: {e}"}


def main():
    if len(sys.argv) < 2:
        print("Usage: python ai_client.py <command>")
        print("Example: python ai_client.py 'rewrite in simpler words'")
        sys.exit(1)
    
    command = ' '.join(sys.argv[1:])
    result = send_command(command)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()