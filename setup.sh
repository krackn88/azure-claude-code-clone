#!/bin/bash

# Azure Claude Code Clone Setup Script

set -e

echo "Setting up Azure Claude Code Clone..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    echo "AZURE_OPENAI_API_KEY=" > .env
    echo "AZURE_OPENAI_ENDPOINT=" >> .env
    echo "AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4" >> .env
    echo "AZCC_HISTORY_FILE=~/.azcc_history" >> .env
    echo "AZCC_MAX_HISTORY=10" >> .env
    echo "AZCC_TEMPERATURE=0.7" >> .env
fi

# Make the CLI tool executable
chmod +x azcc.py

# Ask to configure Azure OpenAI credentials
echo ""
echo "Do you want to configure Azure OpenAI credentials now? (y/n)"
read configure

if [[ $configure == "y" || $configure == "Y" ]]; then
    echo "Enter your Azure OpenAI API key:"
    read api_key
    echo "Enter your Azure OpenAI endpoint URL:"
    read endpoint
    echo "Enter your Azure OpenAI deployment name (default: gpt-4):"
    read deployment
    deployment=${deployment:-gpt-4}
    
    # Update .env file
    sed -i "s|AZURE_OPENAI_API_KEY=.*|AZURE_OPENAI_API_KEY=$api_key|" .env
    sed -i "s|AZURE_OPENAI_ENDPOINT=.*|AZURE_OPENAI_ENDPOINT=$endpoint|" .env
    sed -i "s|AZURE_OPENAI_DEPLOYMENT_NAME=.*|AZURE_OPENAI_DEPLOYMENT_NAME=$deployment|" .env
    
    echo "Azure OpenAI credentials configured."
fi

# Ask to create a symlink
echo ""
echo "Do you want to create a symlink to azcc in /usr/local/bin? (y/n)"
read symlink

if [[ $symlink == "y" || $symlink == "Y" ]]; then
    sudo ln -sf $(pwd)/azcc.py /usr/local/bin/azcc
    echo "Symlink created. You can now use 'azcc' from anywhere."
fi

echo ""
echo "Setup complete! You can start using Azure Claude Code with:"
echo "  ./azcc.py [prompt]"
if [[ $symlink == "y" || $symlink == "Y" ]]; then
    echo "  or simply: azcc [prompt]"
fi
echo ""
echo "For interactive mode, use:"
echo "  ./azcc.py --interactive"
echo ""
echo "For more information, use:"
echo "  ./azcc.py --help"