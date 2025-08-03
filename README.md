# Meeting Summary App

AI-powered meeting transcription and summarization application with premium features and payment integration.

## 🚀 Features

### Core Features
- **Real-time Audio Recording**: Browser-based audio recording with chunking
- **AI Transcription**: High-accuracy transcription using OpenAI Whisper API
- **AI Summarization**: Automatic meeting summarization using ChatGPT API
- **History Management**: View and manage past meeting summaries
- **User Authentication**: Secure user authentication with JWT tokens
- **Google OAuth**: Google account login integration

### Premium Features
- **Extended Recording Time**: 2 hours (vs 30 minutes for free users)
- **PDF Export**: Download summaries as PDF with Japanese font support
- **Word Export**: Download summaries as Word documents
- **Unlimited Usage**: No usage limits for premium users
- **Priority Support**: Enhanced customer support

### Technical Features
- **Rate Limiting**: API abuse prevention
- **Security**: Input validation, CORS, secure file handling
- **Payment Integration**: Stripe payment processing
- **Responsive Design**: Modern, user-friendly interface

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLAlchemy + SQLite
- **AI Services**: OpenAI Whisper + ChatGPT
- **Payment**: Stripe
- **Authentication**: JWT + Google OAuth

### Frontend
- **Framework**: React + TypeScript
- **Styling**: CSS3
- **HTTP Client**: Axios
- **Build Tool**: Vite

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/meeting-summary-app.git
cd meeting-summary-app/backend
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Database Setup**
```bash
python -c "from app.core.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"
```

5. **Run Backend**
```bash
python main.py
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Run Frontend**
```bash
npm run dev
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Stripe Configuration
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Security
SECRET_KEY=your_secret_key
ENCRYPTION_KEY=your_encryption_key

# Features
DUMMY_LOGIN_ENABLED=true
FREE_TRIAL_DAYS=31
FREE_USAGE_LIMIT=10
MONTHLY_PRICE=980
```

## 🚀 Usage

1. **Start the application**
   - Backend: `python main.py` (runs on http://localhost:8000)
   - Frontend: `npm run dev` (runs on http://localhost:3000)

2. **Login**
   - Use Google OAuth login
   - Or use dummy login for testing: `dummy@example.com`

3. **Record a Meeting**
   - Click "録音開始" on the home page
   - Enter meeting title and participants
   - Click "録音開始" to begin recording
   - Click "録音停止" when finished

4. **View Summaries**
   - Go to "履歴" page to view all recordings
   - Click on any recording to view its summary
   - Premium users can export as PDF/Word

## 💳 Payment Integration

### Stripe Setup
1. Create a Stripe account
2. Get your API keys from the Stripe dashboard
3. Configure webhooks for subscription management
4. Update environment variables

### Premium Features
- Extended recording time (2 hours)
- PDF/Word export functionality
- Unlimited usage
- Priority support

## 🔒 Security Features

- **Rate Limiting**: Prevents API abuse
- **Input Validation**: Secure data handling
- **CORS**: Cross-origin resource sharing
- **JWT Authentication**: Secure user sessions
- **File Security**: Secure audio file handling
- **OAuth Integration**: Secure third-party authentication

## 📁 Project Structure

```
meeting-summary-app/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   └── middleware/
│   ├── migrations/
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── contexts/
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for Whisper and ChatGPT APIs
- Stripe for payment processing
- FastAPI for the backend framework
- React for the frontend framework
- Google for OAuth authentication

## 📞 Support

For support, email support@meeting-summary-app.com or create an issue in this repository.

---

**Note**: This is a development version. For production use, ensure proper security configurations and environment setup.
