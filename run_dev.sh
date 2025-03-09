#!/bin/bash

# Navigate to the directory containing the script
cd "$(dirname "$0")" || exit 1

# This script opens two terminal windows:
# Terminal 1: Runs the Python Flask API server on port 8887
# Terminal 2: Runs the Next.js website development server
# Use this multi-terminal setup to monitor both services independently

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    # Start API server in new terminal
    osascript -e 'tell app "Terminal" to do script "cd '"$(pwd)"' && python api/app.py"'
    
    # Start website in another terminal
    osascript -e 'tell app "Terminal" to do script "cd '"$(pwd)"'/website && npm run dev"'

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    # Start API server in new terminal
    gnome-terminal -- bash -c "cd $(pwd) && python api/app.py"
    
    # Start website in another terminal
    gnome-terminal -- bash -c "cd $(pwd)/website && npm run dev"

else
    echo "Unsupported operating system"
    exit 1
fi
