# Hospital Management System with ChatGPT-Style UI

A modern hospital management system with an AI-powered chatbot interface that mimics ChatGPT's design. The system uses Google's Gemini AI for natural language processing and includes a Model Context Protocol (MCP) server for advanced tool integration.

## 🏗️ Architecture

### Backend
- **MCP Server**: Model Context Protocol server for AI tool integration
- **API Server**: Express.js wrapper for HTTP API endpoints
- **Google Gemini AI**: Natural language processing and chat capabilities
- **TypeScript**: Type-safe backend development
- **JSON Storage**: Simple file-based data storage

### Frontend
- **React**: Modern UI framework
- **Tailwind CSS**: Utility-first CSS framework
- **ChatGPT-style Interface**: Professional chat UI with sidebar, messages, and input
- **Responsive Design**: Mobile-friendly interface

## 🚀 Getting Started

### Prerequisites
- Node.js (v18 or higher)
- npm or yarn
- Google AI API key (Gemini)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   - Your `.env` file is already configured with:
   ```
   GEMINI_API_KEY=AIzaSyCh8aivZH2oEtpE8ifopChn0jU400DXnHk
   ```

4. **Build the TypeScript code:**
   ```bash
   npm run server:build
   ```

5. **Start the API server:**
   ```bash
   npm run api:dev
   ```

The backend will start on `http://localhost:3001`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

The frontend will start on `http://localhost:5173` (or another port if 5173 is taken)

## 🎯 Features

### AI Chat Assistant
- **Natural Language Processing**: Powered by Google Gemini 2.0 Flash
- **Context Awareness**: Understands hospital management tasks
- **Tool Integration**: Can execute backend functions through chat

### User Management
- **Create Users**: Add new patient records with validation
- **List Users**: View all registered patients
- **Random Data Generation**: Create test data for development
- **Real-time Updates**: Live data synchronization

### ChatGPT-Style Interface
- **Sidebar Navigation**: Conversation history and management
- **Message Threading**: Clean message display with timestamps
- **Typing Indicators**: Visual feedback during processing
- **Responsive Design**: Works on desktop and mobile
- **Dark/Light Themes**: Professional appearance

## 💬 Chat Commands

### User Management
- `"Show me all users"` - Display all registered patients
- `"Create a new patient"` - Start patient creation flow
- `"Generate fake user data"` - Create test patient records
- `"Create user John Doe with email john@example.com, address 123 Main St, and phone 555-1234"` - Direct user creation

### System Help
- `"Help"` - Show available commands and features
- `"What can you do?"` - Explain system capabilities
- `"How do I create a patient?"` - Get guidance on specific tasks

## 🛠️ API Endpoints

### Chat API
- `POST /api/chat` - Send messages to AI assistant
- `GET /api/users` - Retrieve all users
- `POST /api/tools/create-user` - Create new user
- `POST /api/tools/create-random-user` - Generate random user

### MCP Tools
- `create-user` - Create user with provided details
- `create-random-user` - Generate user with AI-generated fake data
- `get-users` - Retrieve user list

## 📁 Project Structure

```
hospital_management_system/
├── backend/
│   ├── src/
│   │   ├── server.ts          # MCP Server
│   │   ├── client.ts          # MCP Client
│   │   ├── api-server.js      # HTTP API Server
│   │   └── data/
│   │       └── users.json     # User data storage
│   ├── build/                 # Compiled TypeScript
│   ├── package.json
│   ├── tsconfig.json
│   └── .env
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ChatInterface.jsx    # Main chat component
    │   │   ├── ChatSidebar.jsx      # Conversation sidebar
    │   │   ├── ChatHeader.jsx       # Chat header
    │   │   ├── ChatMessages.jsx     # Messages display
    │   │   ├── MessageBubble.jsx    # Individual message
    │   │   ├── LoadingIndicator.jsx # Typing indicator
    │   │   └── ChatInput.jsx        # Message input
    │   ├── services/
    │   │   └── chatService.js       # API communication
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── index.css
    ├── package.json
    ├── vite.config.js
    └── tailwind.config.js
```

## 🔧 Development

### Backend Development
```bash
# Watch mode for TypeScript compilation
npm run server:build:watch

# Start MCP server directly
npm run server:dev

# Start client for testing
npm run client:dev

# Start API server
npm run api:dev
```

### Frontend Development
```bash
# Start with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🎨 UI Features

- **ChatGPT-inspired Design**: Professional, clean interface
- **Real-time Messaging**: Instant chat responses
- **Message History**: Persistent conversation tracking
- **Typing Indicators**: Visual feedback during AI processing
- **Mobile Responsive**: Works on all screen sizes
- **Accessibility**: Keyboard navigation and screen reader support

## 🧪 Testing

### Test the Chat Interface
1. Start both backend and frontend servers
2. Open the frontend in your browser
3. Try these commands:
   - "Help me get started"
   - "Show all users"
   - "Create a random patient"
   - "Add a new patient named John Doe"

### Test API Directly
```bash
# Test chat endpoint
curl -X POST http://localhost:3001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me all users"}'

# Test user creation
curl -X POST http://localhost:3001/api/tools/create-user \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com", "address": "123 Main St", "phone": "555-1234"}'
```

## 🚧 Troubleshooting

### Backend Issues
- **Port 3001 in use**: Change the port in `api-server.js`
- **Gemini API errors**: Check your API key in `.env`
- **Build errors**: Run `npm run server:build` first

### Frontend Issues
- **API connection failed**: Ensure backend is running on port 3001
- **Styling issues**: Check that Tailwind CSS is properly configured
- **Component errors**: Verify all imports are correct

## 🔮 Future Enhancements

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] User authentication and authorization
- [ ] File upload for patient documents
- [ ] Advanced search and filtering
- [ ] Real-time notifications
- [ ] Appointment scheduling
- [ ] Medical records management
- [ ] Integration with hospital systems
- [ ] Multi-language support
- [ ] Voice input/output

## 📄 License

MIT License - feel free to use this project for your own hospital management needs!
