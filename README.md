# Language Factory - AI-Powered Language Learning Platform

## 📖 Tổng quan

Language Factory là một nền tảng học ngôn ngữ thông minh sử dụng AI để tự động tạo ra bài học theo từng chủ đề và trình độ cho nhiều ngôn ngữ (Tiếng Trung, Tiếng Anh, Tiếng Tây Ban Nha). Hệ thống sử dụng CrewAI với nhiều agent chuyên biệt để tạo ra nội dung học tập toàn diện.

## 🎯 Tính năng chính

### 📚 Tạo bài học tự động
- **Nhiều ngôn ngữ:** Hỗ trợ Tiếng Trung (HSK 1-6), Tiếng Anh (CEFR A1-C2), Tiếng Tây Ban Nha (CEFR A1-C2)
- **Nhiều trình độ:** Từ cơ bản đến nâng cao theo từng hệ thống cấp độ chuẩn
- **Nội dung đa dạng:** Mỗi bài học bao gồm:
  - 📋 Mục tiêu bài học (Lesson Objectives)
  - 📖 Bài đọc theo chủ đề (Story/Reading)
  - 📝 Từ vựng theo ngữ cảnh (Vocabulary)
  - 📐 Ngữ pháp trọng tâm (Grammar Points)
  - 📋 Bài tập trắc nghiệm (Quiz)
  - ✍️ Đề bài viết (Writing Prompt)

### 🤖 Hệ thống AI Agents
Hệ thống sử dụng 5 agent chuyên biệt với CrewAI:

1. **Lesson Planner Agent** - Lên kế hoạch bài học
2. **Content Writer Agent** - Viết nội dung bài đọc
3. **Linguist Agent** - Phân tích từ vựng và ngữ pháp
4. **Examiner Agent** - Tạo bài tập kiểm tra
5. **Writing Assessor Agent** - Đề bài viết và chấm điểm

### ✍️ Hệ thống Writing
- **Tự động đề bài:** Generate đề bài viết theo chủ đề và trình độ
- **Chấm điểm tự động:** AI đánh giá bài viết với feedback chi tiết
- **Phản hồi đa chiều:** Đánh giá về ngữ pháp, từ vựng, cấu trúc câu

## 🏗️ Kiến trúc hệ thống

### Frontend (Next.js + TypeScript)
```
app/
├── landing/          # Trang đăng nhập/đăng ký
├── dashboard/        # Dashboard người dùng
├── components/       # Components UI
├── lib/             # Redux store và utilities
└── StoreProvider.tsx # Redux provider
```

### Backend Services

#### Agent Service (Python + FastAPI)
```
ChineseLearning/agent_service/
├── agents.py        # Định nghĩa các AI agents
├── tasks.py         # Định nghĩa tasks cho agents
├── main.py          # Logic orchestration chính
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

## 🚀 Cài đặt và chạy

### Yêu cầu
- Node.js 18+
- Python 3.10+
- PM2 (Process Manager)
- OpenAI API Key

### 1. Clone repository
```bash
git clone <repository-url>
cd HSKGPT
```

### 2. Cài đặt Frontend
```bash
npm install
```

### 3. Cài đặt Backend Dependencies
```bash
# Agent Service
cd ChineseLearning/agent_service
pip install -r requirements.txt

# Auth Service  
cd ../auth_service
pip install -r requirements.txt
```

### 4. Cấu hình Environment Variables
Tạo file `.env` trong `ChineseLearning/agent_service/`:
```env
OPENAI_API_KEY=your_openai_api_key_here
ENVIRONMENT=development
OPTIMIZED_MODEL=gpt-3.5-turbo
PYTHONUNBUFFERED=1
```

### 5. Khởi động Services
```bash
# Khởi động tất cả services với PM2
pm2 start ecosystem.config.js

# Kiểm tra status
pm2 status

# Xem logs
pm2 logs
```

### 6. Chạy Frontend
```bash
npm run dev
```

Truy ứng dụng tại: `http://localhost:3000`

## 📡 API Endpoints

### Agent Service (Port 8000)

#### Tạo bài học
```http
POST /generate
Content-Type: application/json

{
  "topic": "Daily Life",
  "level": "HSK 3", 
  "language": "chinese"
}
```

#### Gợi ý chủ đề
```http
POST /suggest-topic
Content-Type: application/json

{
  "level": "HSK 4",
  "language": "chinese"
}
```

#### Writing - Đề bài
```http
POST /writing/prompt
Content-Type: application/json

{
  "topic": "Technology",
  "level": "HSK 5",
  "language": "chinese"
}
```

#### Writing - Chấm điểm
```http
POST /writing/grade
Content-Type: application/json

{
  "submission": "Nội dung bài viết...",
  "prompt_data": {...},
  "language": "chinese"
}
```

#### Các endpoint khác
- `GET /languages` - Danh sách ngôn ngữ hỗ trợ
- `GET /health` - Kiểm tra sức khỏe service
- `GET /` - Thông tin service

### Auth Service (Port 8001)

#### Authentication
```http
POST /register        # Đăng ký
POST /login           # Đăng nhập
POST /logout          # Đăng xuất
GET  /me              # Thông tin user
```

## 🎨 Flow tạo bài học

### 1. Input từ User
- Chọn ngôn ngữ (Chinese/English/Spanish)
- Chọn trình độ (HSK 1-6 hoặc CEFR A1-C2)
- Nhập chủ đề hoặc để tự động gợi ý

### 2. AI Processing Pipeline
```
Topic Suggestion (nếu cần)
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
- **Markdown content** - Nội dung đầy đủ
- **Interactive HTML** - Giao diện học tập tương tác
- **JSON data** - Dữ liệu cấu trúc cho frontend
- **Files saved** - Lưu trữ local (.md, .html, .json)

## 🧠 AI Agents Chi tiết

### 1. Lesson Planner Agent
- **Vai trò:** Lên kế hoạch cấu trúc bài học
- **Output:** Mục tiêu, từ vựng chính, điểm ngữ pháp
- **Model:** GPT-3.5-turbo, temperature=0.3

### 2. Content Writer Agent  
- **Vai trò:** Viết bài đọc theo chủ đề
- **Output:** Story/content 200-1200 từ tùy trình độ
- **Model:** GPT-3.5-turbo, temperature=0.8

### 3. Linguist Agent
- **Vai trò:** Phân tích ngôn ngữ học
- **Output:** Danh sách từ vựng, giải thích ngữ pháp
- **Model:** GPT-3.5-turbo, temperature=0.2

### 4. Examiner Agent
- **Vai trò:** Tạo bài tập kiểm tra
- **Output:** Quiz trắc nghiệm, điền khuyết
- **Model:** GPT-3.5-turbo, temperature=0.4

### 5. Writing Assessor Agent
- **Vai trò:** Đề bài và chấm điểm writing
- **Output:** Writing prompts, detailed feedback
- **Model:** GPT-3.5-turbo, temperature=0.5

## 📊 Performance Optimization

### Caching System
- **Memory Cache:** TTL 30 phút cho recent requests
- **File Cache:** Persistent storage cho cache
- **Cache Hit Rate:** ~80-90% cho repeated requests

### Request Management
- **Queue System:** Priority queue với max 2 concurrent requests
- **Load Balancing:** Auto-scaling based on system load
- **Timeout Handling:** 10 phút timeout cho lesson generation

### Monitoring
- **Performance Metrics:** Response time, success rate, error tracking
- **System Health:** CPU, Memory, Disk monitoring
- **Cache Analytics:** Hit rate, efficiency tracking

## 🔧 Development

### Frontend Technologies
- **Framework:** Next.js 14 with App Router
- **Language:** TypeScript
- **State Management:** Redux Toolkit
- **Styling:** Tailwind CSS
- **UI Components:** Custom components với Lucide icons

### Backend Technologies  
- **Framework:** FastAPI (Python)
- **AI Framework:** CrewAI
- **Database:** SQLAlchemy (SQLite/PostgreSQL)
- **Authentication:** JWT
- **Process Management:** PM2

### AI/ML Stack
- **LLM:** OpenAI GPT-3.5-turbo/GPT-4
- **Agent Framework:** CrewAI
- **Prompt Engineering:** Optimized prompts cho từng agent type
- **Token Optimization:** Efficient token usage

## 📈 Performance Metrics

### Response Times
- **Cache Hit:** <1 giây
- **Normal Request:** 15-25 giây (tối ưu 60-70% so với trước)
- **Queued Request:** 2-5 phút tùy load

### System Capacity
- **Concurrent Users:** 50-100 active users
- **Daily Lessons:** 500-1000 lessons
- **Cache Storage:** 50MB-100MB

## 🛠️ Troubleshooting

### Common Issues

#### Service không khởi động
```bash
# Kiểm tra logs
pm2 logs agent-service

# Restart service
pm2 restart agent-service

# Kiểm tra port
netstat -an | grep 8000
```

#### Lỗi CrewAI/Python
```bash
# Kiểm tra Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

#### Frontend không kết nối được API
```bash
# Kiểm tra API status
curl http://localhost:8000/health

# Kiểm tra CORS configuration
# Đảm bảo agent-service đang chạy
```

### Debug Mode
```bash
# Chạy agent service trong debug mode
cd ChineseLearning/agent_service
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Chạy auth service trong debug mode  
cd ../auth_service
uvicorn api:app --reload --host 0.0.0.0 --port 8001
```

## 📝 Logging & Monitoring

### Log Files
- **Agent Service:** `logs/agent-service-*.log`
- **Auth Service:** `logs/auth-service-*.log`
- **PM2 Logs:** `pm2 logs [service-name]`

### Performance Monitoring
```bash
# Check performance stats
curl http://localhost:8000/performance/stats

# Check queue status
curl http://localhost:8000/queue/stats
```

## 🚀 Deployment

### Production Setup
1. **Environment Variables:** Cấu hình production keys
2. **Database:** Setup PostgreSQL cho production
3. **Load Balancer:** Nginx/Apache cho frontend
4. **SSL:** HTTPS certificates
5. **Monitoring:** Setup alerts cho system health

### PM2 Production Commands
```bash
# Start production
pm2 start ecosystem.config.js --env production

# Save PM2 config
pm2 save

# Setup startup script
pm2 startup
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Backend Developer:** AI/Python Engineer
- **Frontend Developer:** React/Next.js Developer  
- **AI Specialist:** Prompt Engineering & CrewAI Expert
- **DevOps:** System Administration & Deployment

## 📞 Support

For support and questions:
- Create Issue in GitHub repository
- Email: support@languagefactory.com
- Documentation: [Wiki](link-to-wiki)

---

**Language Factory** - Transform Language Learning with AI 🚀
