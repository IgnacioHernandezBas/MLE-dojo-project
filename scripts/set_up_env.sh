#!/bin/bash
# Source this before running singularity commands

# Unset problematic vars
unset KAGGLE_CONFIG_DIR KAGGLE_DATA_DIR

# Read .env and export as SINGULARITYENV_ variables
while IFS='=' read -r key value; do
    # Skip empty lines and comments
    [[ -z "$key" || "$key" =~ ^#.*$ ]] && continue
    
    # Remove quotes from value
    value=$(echo "$value" | sed 's/^"//;s/"$//')
    
    # Export with SINGULARITYENV_ prefix
    export "SINGULARITYENV_${key}=${value}"
    echo "Exported: ${key}"
done < .env

echo "✓ Environment ready for Singularity"