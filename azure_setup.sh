#!/bin/bash

# Azure OpenAI Setup Script for Azure VM

set -e

echo "Setting up Azure OpenAI on your VM..."

# Install Azure CLI if not already installed
if ! command -v az &> /dev/null; then
    echo "Installing Azure CLI..."
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
fi

# Log in to Azure
echo "Logging in to Azure..."
az login --use-device-code

# List available subscriptions
echo "Available subscriptions:"
az account list --output table

# Ask which subscription to use
echo "Enter the subscription ID to use:"
read subscription_id

# Set the subscription
az account set --subscription "$subscription_id"

# Check if OpenAI is already set up
echo "Checking for existing Azure OpenAI resources..."
openai_resources=$(az cognitiveservices account list --query "[?kind=='OpenAI']")

if [ "$openai_resources" == "[]" ]; then
    echo "No Azure OpenAI resources found. Creating a new one..."
    
    # Get available regions
    echo "Available regions for Azure OpenAI:"
    az provider show --namespace Microsoft.CognitiveServices --query "resourceTypes[?resourceType=='accounts'].locations[] | [0]" --out table
    
    echo "Enter the region to create the resource in (e.g., eastus):"
    read region
    
    echo "Enter a name for your Azure OpenAI resource:"
    read resource_name
    
    echo "Enter the resource group name:"
    read resource_group
    
    # Create the resource
    echo "Creating Azure OpenAI resource..."
    az cognitiveservices account create \
        --name "$resource_name" \
        --resource-group "$resource_group" \
        --kind OpenAI \
        --sku S0 \
        --location "$region"
    
    # Get the key and endpoint
    key=$(az cognitiveservices account keys list \
        --name "$resource_name" \
        --resource-group "$resource_group" \
        --query key1 \
        --output tsv)
    
    endpoint=$(az cognitiveservices account show \
        --name "$resource_name" \
        --resource-group "$resource_group" \
        --query properties.endpoint \
        --output tsv)
    
    # Create a deployment
    echo "Enter a name for your model deployment (e.g., gpt4):"
    read deployment_name
    
    echo "Creating model deployment..."
    az cognitiveservices account deployment create \
        --name "$resource_name" \
        --resource-group "$resource_group" \
        --deployment-name "$deployment_name" \
        --model-name "gpt-4" \
        --model-version "0613" \
        --model-format "OpenAI"
    
    echo "Azure OpenAI resource created successfully."
else
    echo "Found existing Azure OpenAI resources."
    echo "Select a resource to use:"
    
    # Display available resources
    az cognitiveservices account list --query "[?kind=='OpenAI'].[name, location, resourceGroup]" --output table
    
    echo "Enter the name of the resource to use:"
    read resource_name
    
    echo "Enter the resource group of the selected resource:"
    read resource_group
    
    # Get the key and endpoint
    key=$(az cognitiveservices account keys list \
        --name "$resource_name" \
        --resource-group "$resource_group" \
        --query key1 \
        --output tsv)
    
    endpoint=$(az cognitiveservices account show \
        --name "$resource_name" \
        --resource-group "$resource_group" \
        --query properties.endpoint \
        --output tsv)
    
    # List deployments
    echo "Available deployments:"
    az cognitiveservices account deployment list \
        --name "$resource_name" \
        --resource-group "$resource_group" \
        --output table
    
    echo "Enter the deployment name to use:"
    read deployment_name
fi

# Update the .env file in the azcc directory
echo "Updating Azure Claude Code configuration..."
cd ~/azure-claude-code-clone

sed -i "s|AZURE_OPENAI_API_KEY=.*|AZURE_OPENAI_API_KEY=$key|" .env
sed -i "s|AZURE_OPENAI_ENDPOINT=.*|AZURE_OPENAI_ENDPOINT=$endpoint|" .env
sed -i "s|AZURE_OPENAI_DEPLOYMENT_NAME=.*|AZURE_OPENAI_DEPLOYMENT_NAME=$deployment_name|" .env

echo "Setup complete! Your Azure Claude Code Clone is now configured to use Azure OpenAI."