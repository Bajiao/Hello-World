#!/bin/bash
# api_key_setup.sh - Set up OpenAI API key consistently

NEW_API_KEY="<your openai key>"

echo "🔑 Setting up OpenAI API Key..."
echo "   New API Key: ${NEW_API_KEY:0:20}...${NEW_API_KEY: -10}"

# Option 1: Set for current session
export OPENAI_API_KEY="$NEW_API_KEY"
echo "✅ API Key set for current session"

# Option 2: Add to .zshrc for persistence
if grep -q "OPENAI_API_KEY" ~/.zshrc; then
    echo "📝 Updating existing OPENAI_API_KEY in ~/.zshrc"
    sed -i '' "s|export OPENAI_API_KEY=.*|export OPENAI_API_KEY=\"$NEW_API_KEY\"|g" ~/.zshrc
else
    echo "📝 Adding OPENAI_API_KEY to ~/.zshrc"
    echo "export OPENAI_API_KEY=\"$NEW_API_KEY\"" >> ~/.zshrc
fi

# Verify
echo ""
echo "🔍 Verification:"
echo "   Current session OPENAI_API_KEY: ${OPENAI_API_KEY:0:20}...${OPENAI_API_KEY: -10}"

if grep -q "$NEW_API_KEY" ~/.zshrc; then
    echo "   ✅ API Key saved to ~/.zshrc"
else
    echo "   ⚠️  API Key NOT found in ~/.zshrc - May need manual update"
fi

echo ""
echo "Ready to run: python3 backend_menu_processing/comprehensive_benchmark.py"
