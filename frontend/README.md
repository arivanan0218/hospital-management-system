# Hospital AI Assistant Frontend

A modern React-based chatbot interface that integrates **Claude AI** or **Google Gemini AI** with a Hospital Management System through an MCP (Model Context Protocol) bridge.

## Features

- 🤖 **AI-Powered Chat**: Uses Claude AI (recommended) or Google Gemini AI for intelligent responses
- 🏥 **Hospital Integration**: Direct connection to hospital management system via MCP bridge
- ⚡ **Quick Actions**: Predefined buttons for common hospital operations
- 📊 **Data Visualization**: Interactive tables and formatted data display
- 🔄 **Real-time Status**: Live connection status with the MCP bridge
- 💾 **Persistent Settings**: API key storage in localStorage
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🔧 **Dual AI Support**: Choose between Claude (recommended) or Gemini AI

## Prerequisites

1. **Node.js** (v16 or higher)
2. **AI API Key** - Choose one:
   - **Claude API Key** (Recommended) - Get from [Anthropic Console](https://console.anthropic.com/)
   - **Google Gemini API Key** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
3. **MCP Bridge Server** - Should be running on `http://localhost:8080`

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### 3. Configure API Key

**Option A: Using .env file (Recommended)**
1. Copy `.env.example` to `.env`
2. Choose your AI service and add the appropriate API key:
   ```bash
   # For Claude AI (Recommended)
   VITE_CLAUDE_API_KEY=your_claude_api_key_here
   
   # OR for Google Gemini
   VITE_GOOGLE_API_KEY=your_gemini_api_key_here
   ```

**Option B: Using the Settings UI**
1. Click the **Settings** button (⚙️) in the top-right
2. Select your preferred AI service (Claude or Gemini)
3. Enter your API key
4. The key will be saved in your browser's localStorage

**Option C: Environment Variable**
```powershell
# PowerShell - Claude
$env:VITE_CLAUDE_API_KEY="your_claude_api_key_here"

# PowerShell - Gemini  
$env:VITE_GOOGLE_API_KEY="your_gemini_api_key_here"

# Command Prompt - Claude
set VITE_CLAUDE_API_KEY=your_claude_api_key_here

# Command Prompt - Gemini
set VITE_GOOGLE_API_KEY=your_gemini_api_key_here
```

### 4. Start Chatting

- Use the quick action buttons for common queries
- Type natural language questions about hospital operations
- The AI will automatically query the hospital system when needed

## Available Quick Actions

- **List Patients** - View all registered patients
- **Available Beds** - Find open beds for new admissions  
- **Today's Appointments** - View scheduled appointments for today
- **Low Stock Supplies** - Check inventory levels
- **Staff Members** - View hospital staff directory
- **Equipment Status** - Check equipment availability

## Example Queries

Here are some example questions you can ask:

### Patient Management
- "Show me all patients"
- "Find patients with blood type O+"
- "Who are the patients in the ICU?"

### Bed Management
- "How many beds are available?"
- "Show me occupied beds"
- "Find available beds in the cardiology department"

### Staff Operations
- "List all doctors"
- "Show me nurses on duty"
- "Who works in the emergency department?"

### Equipment & Supplies
- "What equipment needs maintenance?"
- "Show me low stock medications"
- "List all X-ray machines"

### Appointments
- "Show today's appointments"
- "Find appointments for Dr. Smith"
- "What appointments are scheduled for tomorrow?"

## Architecture

```
React Frontend → Gemini AI ↔ MCP Bridge → Hospital Management System
```

The frontend is designed to work independently while connecting to the hospital management system through the MCP bridge, similar to how Claude AI works as a standalone interface.+ Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
