# Language Factory - AI-Powered Language Learning Platform

## 📖 Overview

Language Factory is an intelligent language learning platform that uses AI to automatically generate personalized lessons based on topics and proficiency levels for multiple languages (Chinese, English, Spanish). The system utilizes CrewAI with specialized agents to create comprehensive educational content.

## 🎯 Key Features

### 📚 Automatic Lesson Generation
- **Multilingual Support:** Supports Chinese (HSK 1-6), English (CEFR A1-C2), and Spanish (CEFR A1-C2).
- **Multiple Proficiency Levels:** From beginner to advanced, following standardized level systems.
- **Comprehensive Content:** Each lesson includes:
  - 📋 Lesson Objectives
  - 📖 Thematic Reading (Story/Reading Passage)
  - 📝 Contextual Vocabulary
  - 📐 Grammar Focus points
  - 📋 Interactive Quizzes
  - ✍️ Writing Prompts

### 🤖 AI Agent System
The system employs 5 specialized agents using CrewAI:

1. **Lesson Planner Agent** - Plans the lesson structure and objectives.
2. **Content Writer Agent** - Dynamically writes the reading material.
3. **Linguist Agent** - Analyzes vocabulary and explains grammar points.
4. **Examiner Agent** - Creates assessment quizzes.
5. **Writing Assessor Agent** - Generates writing prompts and provides detailed grading.

### ✍️ Writing System
- **Automatic Prompt Generation:** Creates writing tasks aligned with the lesson topic and level.
- **Automated Grading:** AI evaluates submissions with detailed feedback.
- **Multi-dimensional Feedback:** Assessment covers grammar, vocabulary usage, and sentence structure.

## 🏗️ System Architecture

### Frontend (Next.js + TypeScript)
```
app/
├── landing/          # Login/Signup pages
├── dashboard/        # User dashboard
├── components/       # UI Components
├── lib/             # Redux store and utilities
└── StoreProvider.tsx # Redux provider
```

### Backend Services

#### Agent Service (Python + FastAPI)
```
ChineseLearning/agent_service/
├── agents.py        # AI agents definitions
├── tasks.py         # Task definitions for agents
├── main.py          # Main orchestration logic
├── api.py           # FastAPI endpoints
├── cache.py         # Caching mechanism
├── monitoring.py    # Performance monitoring
├── queue.py         # Request queue management
└── optimization.py  # Model optimization
```

#### Auth Service (Python + FastAPI)
```
ChineseLearning/auth_service/
├── api.py           # Authentication endpoints
├── database.py      # Database models
├── auth.py          # JWT authentication
└── middleware.py    # Auth middleware
```

## 🚀 Installation & Setup

### Prerequisites
- Node.js 18+
- Python 3.10+
- PM2 (Process Manager)
- OpenAI API Key

### 1. Clone the Repository
```bash
git clone <repository-url>
cd HSKGPT
```

### 2. Frontend Setup
```bash
npm install
```

### 3. Backend Dependencies Setup
```bash
# Agent Service
cd ChineseLearning/agent_service
pip install -r requirements.txt

# Auth Service  
cd ../auth_service
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in `ChineseLearning/agent_service/`:
```env
OPENAI_API_KEY=your_openai_api_key_here
ENVIRONMENT=development
OPTIMIZED_MODEL=gpt-3.5-turbo
PYTHONUNBUFFERED=1
```

### 5. Start Services with PM2
```bash
# Start all services using ecosystem configuration
pm2 start ecosystem.config.js

# Check service status
pm2 status

# Monitor logs
pm2 logs
```

### 6. Run Frontend
```bash
npm run dev
```

The application will be available at: `http://localhost:3000`

## 📡 API Endpoints

### Agent Service (Port 8000)

#### Lesson Generation
```http
POST /generate
Content-Type: application/json

{
  "topic": "Daily Life",
  "level": "HSK 3", 
  "language": "chinese"
}
```

#### Topic Suggestion
```http
POST /suggest-topic
Content-Type: application/json

{
  "level": "HSK 4",
  "language": "chinese"
}
```

#### Writing - Prompt Generation
```http
POST /writing/prompt
Content-Type: application/json

{
  "topic": "Technology",
  "level": "HSK 5",
  "language": "chinese"
}
```

#### Writing - Grading
```http
POST /writing/grade
Content-Type: application/json

{
  "submission": "Your essay content...",
  "prompt_data": {...},
  "language": "chinese"
}
```

#### Other Endpoints
- `GET /languages` - List of supported languages.
- `GET /health` - Service health check.
- `GET /` - Basic service information.

### Auth Service (Port 8001)

#### Authentication
```http
POST /register        # User Registration
POST /login           # User Login
POST /logout          # Log out
GET  /me              # Get Current User Information
```

## 🎨 Lesson Creation Flow

### 1. User Input
- Select Language (Chinese/English/Spanish)
- Select Level (HSK 1-6 or CEFR A1-C2)
- Enter a topic or use the automatic suggestion tool

### 2. AI Processing Pipeline
```
Topic Suggestion (Optional)
        ↓
    Lesson Planning
        ↓
    Content Writing
        ↓
   Language Analysis
        ↓
     Quiz Creation
        ↓
    Writing Prompt
```

### 3. Output
- **Markdown Content** - Full lesson text for reference.
- **Interactive HTML** - Dynamic interface for an engaging learning experience.
- **JSON Data** - Structured data for frontend rendering.
- **Local Storage** - Files saved as .md, .html, and .json.

## 🧠 Detailed AI Agents

### 1. Lesson Planner Agent
- **Role:** Designs the lesson architecture.
- **Output:** Learning objectives, key vocabulary list, and grammar focuses.
- **Model:** GPT-3.5-turbo (Temp: 0.3)

### 2. Content Writer Agent  
- **Role:** Authors the thematic reading content.
- **Output:** Engaging stories/passages (200-1200 words depending on level).
- **Model:** GPT-3.5-turbo (Temp: 0.8)

### 3. Linguist Agent
- **Role:** Performs linguistic analysis.
- **Output:** Vocabulary definitions and grammatical explanations.
- **Model:** GPT-3.5-turbo (Temp: 0.2)

### 4. Examiner Agent
- **Role:** Develops assessment materials.
- **Output:** Multiple-choice and fill-in-the-blank quizzes.
- **Model:** GPT-3.5-turbo (Temp: 0.4)

### 5. Writing Assessor Agent
- **Role:** Manages writing assessments.
- **Output:** Thematic writing prompts and detailed corrective feedback.
- **Model:** GPT-3.5-turbo (Temp: 0.5)

## 📊 Performance Optimization

### Caching System
- **Memory Cache:** 30-minute TTL for frequent requests.
- **File Cache:** Persistent storage for long-term caching.
- **Cache Hit Rate:** ~80-90% for repeated requests.

### Request Management
- **Queue System:** Priority-based queueing with 2 concurrent requests max.
- **Load Balancing:** Dynamic scaling based on system load.
- **Timeout Handling:** 10-minute maximum for full lesson generation.

### Monitoring
- **Performance Metrics:** Tracks response times, success rates, and errors.
- **System Health:** Continuous monitoring of CPU, RAM, and Disk usage.
- **Cache Analytics:** Monitors hit rates and optimization efficiency.

## 🔧 Development Stack

### Frontend Technologies
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **State Management:** Redux Toolkit
- **Styling:** Tailwind CSS
- **Iconography:** Lucide React

### Backend Technologies  
- **Framework:** FastAPI (Python)
- **AI Framework:** CrewAI
- **Database:** SQLAlchemy (SQLite/PostgreSQL)
- **Security:** JWT Authentication
- **Process Management:** PM2

### AI/ML Stack
- **Models:** OpenAI GPT-3.5-turbo / GPT-4
- **Prompt Engineering:** Specialized, optimized prompt templates per agent.
- **Efficiency:** Optimized token usage for cost and speed.

## 📈 Performance Benchmarks

### Response Times
- **Cache Hit:** < 1 second
- **Standard Generation:** 15-25 seconds (60-70% improvement over initial versions)
- **Queued Tasks:** 2-5 minutes depending on concurrent load

### System Capacity
- **Concurrent Users:** 50-100 active users
- **Daily Throughput:** 500-1000 lessons
- **Cache Footprint:** 50MB-100MB

## 🛠️ Troubleshooting

### Common Issues

#### Services Fail to Start
```bash
# Check service logs
pm2 logs agent-service

# Restart the service
pm2 restart agent-service

# Verify port availability
netstat -an | findstr :8000
```

#### Python/CrewAI Errors
```bash
# Verify Python version
python --version  # Must be 3.10+

# Force reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

#### Frontend Cannot Connect to API
```bash
# Test API locally
curl http://localhost:8000/health

# Check CORS settings in Backend
# Ensure agent-service is currently running
```

### Debug Mode
```bash
# Run Agent Service in reload mode
cd ChineseLearning/agent_service
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Run Auth Service in reload mode
cd ../auth_service
uvicorn api:app --reload --host 0.0.0.0 --port 8001
```

## 📝 Logging & Monitoring

### Log Locations
- **Agent Service Logs:** `logs/agent-service-*.log`
- **Auth Service Logs:** `logs/auth-service-*.log`
- **PM2 Centralized Logs:** `pm2 logs [service-name]`

### Metrics Endpoints
- **Performance Stats:** `GET http://localhost:8000/performance/stats`
- **Queue Status:** `GET http://localhost:8000/queue/stats`

## 🚀 Deployment

### Production Setup
1. **Environment Variables:** Secure production keys and environment flags.
2. **Database:** Switch to PostgreSQL for reliable production storage.
3. **Web Server:** Use Nginx/Apache as a reverse proxy for the frontend.
4. **Security:** Implement SSL/TLS certificates (HTTPS).
5. **Alerting:** Configure threshold-based system health alerts.

### PM2 Production Operations
```bash
# Start with production environment
pm2 start ecosystem.config.js --env production

# Persist current processes
pm2 save

# Configure OS startup hook
pm2 startup
```

## 🤝 Contributing

1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 The Team

- **Backend Development:** AI & Python Engineers
- **Frontend Development:** React & Next.js Specialists
- **AI Integration:** Prompt Engineering & CrewAI Experts
- **Infrastructure:** DevOps & System Administration

## 📞 Support

For any questions or issues:
- Open an Issue on the GitHub repository.
- Email: support@languagefactory.com
- Visit the [Project Wiki](link-to-wiki) for more detailed documentation.

---

**Language Factory** - Empowering Language Learning through AI 🚀
