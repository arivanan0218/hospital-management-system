#!/bin/bash

# Make shell scripts executable
chmod +x setup-aws-infrastructure.sh
chmod +x setup-aws-simple.sh
chmod +x setup-local.sh

echo "✅ Shell scripts are now executable"
echo ""
echo "🚀 Ready to deploy! Choose your deployment method:"
echo ""
echo "1. 📦 Local Development:"
echo "   ./setup-local.sh"
echo ""
echo "2. ☁️  AWS Production (Simple):"
echo "   ./setup-aws-simple.sh"
echo ""
echo "3. ☁️  AWS Production (Full):"
echo "   ./setup-aws-infrastructure.sh"
echo ""
echo "📚 For detailed instructions, see DEPLOYMENT.md"
