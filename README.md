# Azure Claude Code Clone

A CLI tool similar to Claude Code built with Azure OpenAI Services, designed for student Azure accounts.

## Overview

This project creates a command-line interface (CLI) tool that mimics the functionality of Claude Code using Azure OpenAI services. The tool allows developers to interact with AI for code generation, explanation, and assistance directly from the terminal.

## Features

- Code generation and completion
- Code explanation and documentation
- Contextual conversations about code
- History tracking of interactions
- Project-specific context management

## Prerequisites

- Python 3.8+
- Azure account with OpenAI services access
- Azure CLI configured

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/krackn88/azure-claude-code-clone.git
cd azure-claude-code-clone
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Azure OpenAI credentials

Create a `.env` file in the project root with your Azure OpenAI credentials:

```
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
```

OR use the setup script:

```bash
./setup.sh
```

### 4. Make the CLI tool executable

```bash
chmod +x azcc.py
```

### 5. Create a symlink (optional)

```bash
sudo ln -s $(pwd)/azcc.py /usr/local/bin/azcc
```

## Usage

### Basic Commands

```bash
# Get code suggestions
azcc "Create a function to calculate Fibonacci numbers"

# Explain code
azcc explain "code_to_explain.py"

# Start an interactive session
azcc interactive

# Get help
azcc --help
```

### Advanced Features

```bash
# Set project context
azcc --context "./my_project"

# Continue from previous conversation
azcc --continue "How would I optimize this code?"

# Export conversation history
azcc --export "session_log.json"
```

## Running on Azure VM

This tool is designed to run on Azure VMs, including the Standard_B1s size with Ubuntu 22.04.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT