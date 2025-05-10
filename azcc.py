#!/usr/bin/env python3

'''
Azure Claude Code Clone (AZCC)
A CLI tool similar to Claude Code built with Azure OpenAI Services
'''

import os
import sys
import json
import argparse
import datetime
import pickle
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax

# Initialize rich console for pretty output
console = Console()

# Load environment variables
load_dotenv()

class AzureClaudeCode:
    def __init__(self):
        # Load config
        self.config = self._load_config()
        
        # Initialize OpenAI client
        self._init_client()
        
        # Load conversation history
        self.history = self._load_history()
        
        # Current project context
        self.context = None

    def _load_config(self):
        """Load configuration from .env file"""
        config = {
            'api_key': os.getenv('AZURE_OPENAI_API_KEY'),
            'endpoint': os.getenv('AZURE_OPENAI_ENDPOINT'),
            'deployment': os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4'),
            'history_file': os.getenv('AZCC_HISTORY_FILE', os.path.expanduser('~/.azcc_history')),
            'max_history': int(os.getenv('AZCC_MAX_HISTORY', 10)),
            'temperature': float(os.getenv('AZCC_TEMPERATURE', 0.7)),
        }
        
        # Check for required values
        if not config['api_key'] or not config['endpoint']:
            console.print("[bold red]Error:[/bold red] Azure OpenAI API credentials not found.")
            console.print("Please run setup.sh or create a .env file with your credentials.")
            sys.exit(1)
            
        return config

    def _init_client(self):
        """Initialize Azure OpenAI client"""
        try:
            self.client = AzureOpenAI(
                api_key=self.config['api_key'],  
                azure_endpoint=self.config['endpoint'],
                api_version="2023-05-15"
            )
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] Failed to initialize Azure OpenAI client: {e}")
            sys.exit(1)

    def _load_history(self):
        """Load conversation history from file"""
        history_path = Path(self.config['history_file'])
        if history_path.exists():
            try:
                with open(history_path, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                return []
        return []

    def _save_history(self):
        """Save conversation history to file"""
        history_path = Path(self.config['history_file'])
        history_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(history_path, 'wb') as f:
            pickle.dump(self.history[-self.config['max_history']:], f)

    def set_context(self, context_path):
        """Set project context by analyzing files in the given path"""
        if not Path(context_path).exists():
            console.print(f"[bold yellow]Warning:[/bold yellow] Context path '{context_path}' does not exist.")
            return
            
        # Get all code files in the directory
        code_files = []
        for ext in ['.py', '.js', '.java', '.cpp', '.h', '.cs', '.go', '.rs', '.ts', '.html', '.css']:
            code_files.extend(Path(context_path).glob(f'**/*{ext}'))
            
        context_content = []
        for file in code_files[:5]:  # Limit to 5 files to avoid token limits
            try:
                with open(file, 'r') as f:
                    content = f.read()
                    if len(content) > 1000:  # Truncate long files
                        content = content[:1000] + '...'
                    context_content.append(f"File: {file.relative_to(context_path)}\n```\n{content}\n```")
            except Exception:
                pass
                
        if context_content:
            self.context = "\n\n".join(context_content)
            console.print(f"[green]Context set with {len(code_files)} files from {context_path}[/green]")
        else:
            console.print("[yellow]No code files found in the specified path.[/yellow]")

    def generate_response(self, prompt, continue_conversation=False, stream=True):
        """Generate a response using Azure OpenAI"""
        # Prepare messages
        messages = []
        
        # System message with instruction
        system_message = {
            "role": "system",
            "content": "You are AzureCC, a command-line AI assistant specialized in helping with code. "
                       "Provide concise, practical responses focused on code solutions. "
                       "Use markdown for formatting. For code, always specify the language. "
                       "When explaining code, be clear and brief. "
        }
        
        # Add project context if available
        if self.context and not continue_conversation:
            system_message["content"] += f"\n\nProject context:\n{self.context}"
            
        messages.append(system_message)
        
        # Add conversation history for continuity
        if continue_conversation and self.history:
            messages.extend(self.history[-3:])  # Add last 3 exchanges for context
            
        # Add the current prompt
        messages.append({"role": "user", "content": prompt})
        
        try:
            # Generate response
            if stream:
                return self._stream_response(messages)
            else:
                response = self.client.chat.completions.create(
                    model=self.config['deployment'],
                    messages=messages,
                    temperature=self.config['temperature'],
                )
                return response.choices[0].message.content
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            return None

    def _stream_response(self, messages):
        """Stream the response from the API"""
        try:
            full_response = ""
            response_stream = self.client.chat.completions.create(
                model=self.config['deployment'],
                messages=messages,
                temperature=self.config['temperature'],
                stream=True,
            )
            
            # Process the streaming response
            for chunk in response_stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    print(content, end='', flush=True)
                    
            print("\n")
            return full_response
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {e}")
            return None

    def interactive_mode(self):
        """Start an interactive session"""
        console.print("[bold green]Starting interactive AzureCC session. Type 'exit' or 'quit' to end.[/bold green]")
        console.print("[bold green]Type 'context <path>' to set project context.[/bold green]")
        
        session_history = []
        
        while True:
            try:
                # Get user input
                user_input = input("\n[azcc]> ")
                
                # Handle exit commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break
                    
                # Handle context setting
                if user_input.lower().startswith('context '):
                    context_path = user_input[8:].strip()
                    self.set_context(context_path)
                    continue
                    
                # Generate and display response
                response = self.generate_response(user_input, continue_conversation=True)
                
                if response:
                    # Add to session history
                    session_history.append({"role": "user", "content": user_input})
                    session_history.append({"role": "assistant", "content": response})
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Session terminated by user.[/yellow]")
                break
                
        # Update global history with this session
        if session_history:
            self.history.extend(session_history)
            self._save_history()
            console.print(f"[green]Session history saved with {len(session_history)//2} exchanges.[/green]")

    def export_history(self, output_file):
        """Export conversation history to a file"""
        if not self.history:
            console.print("[yellow]No history to export.[/yellow]")
            return
            
        try:
            with open(output_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            console.print(f"[green]History exported to {output_file}[/green]")
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] Failed to export history: {e}")

    def explain_code(self, file_path):
        """Explain code from a file"""
        try:
            with open(file_path, 'r') as f:
                code = f.read()
                
            if len(code) > 4000:  # Truncate very large files
                console.print("[yellow]File is very large, truncating to first 4000 characters for analysis.[/yellow]")
                code = code[:4000] + "\n...\n(file truncated)"
                
            prompt = f"Explain this code concisely:\n```\n{code}\n```"
            return self.generate_response(prompt)
                
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            return None

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Azure Claude Code - AI-powered coding assistant')
    
    # Main argument (prompt or command)
    parser.add_argument('prompt', nargs='?', help='The prompt or command to send to the AI')
    
    # Mode selection
    parser.add_argument('-i', '--interactive', action='store_true', help='Start an interactive session')
    parser.add_argument('-e', '--explain', metavar='FILE', help='Explain the code in the specified file')
    
    # Context and history management
    parser.add_argument('-c', '--context', metavar='PATH', help='Set project context from a directory')
    parser.add_argument('--continue', action='store_true', dest='continue_conversation', 
                      help='Continue from previous conversation')
    parser.add_argument('--export', metavar='FILE', help='Export conversation history to a file')
    
    # Output control
    parser.add_argument('--no-stream', action='store_true', help='Disable streaming response')
    
    # Version
    parser.add_argument('-v', '--version', action='store_true', help='Show version information')
    
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Show version and exit
    if args.version:
        console.print("Azure Claude Code (AZCC) v0.1.0")
        return 0
        
    # Initialize the app
    app = AzureClaudeCode()
    
    # Export history if requested
    if args.export:
        app.export_history(args.export)
        return 0
        
    # Set context if provided
    if args.context:
        app.set_context(args.context)
    
    # Handle different modes
    if args.interactive:
        app.interactive_mode()
    elif args.explain:
        app.explain_code(args.explain)
    elif args.prompt:
        response = app.generate_response(
            args.prompt,
            continue_conversation=args.continue_conversation,
            stream=not args.no_stream
        )
        
        if response and args.continue_conversation:
            # Save to history
            app.history.append({"role": "user", "content": args.prompt})
            app.history.append({"role": "assistant", "content": response})
            app._save_history()
    else:
        console.print("[yellow]No command specified. Try --help for usage information.[/yellow]")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())