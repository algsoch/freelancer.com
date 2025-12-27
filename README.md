# AI Bid Writer Agent

An intelligent AI agent with a beautiful web interface that analyzes freelance project descriptions and generates winning bids automatically. **Now powered by Google Gemini (FREE!) by default!**

## 🎯 Features

- 🤖 **AI-Powered Analysis**: Uses Google Gemini, GPT-4, or Claude for intelligent bid generation
- 🆓 **FREE by Default**: Google Gemini API is free and powerful (no credit card required!)
- 💻 **Modern Web UI**: Beautiful React interface with real-time bid generation
- ✨ **Smart Mode**: Just paste the entire project page - automatic extraction of all details
- 📊 **Live Extraction Process**: See real-time progress as your bid is being generated
- 🎯 **Skill Matching**: Automatically highlights relevant experience
- 📈 **Bid Optimization**: AI-powered suggestions to improve your bids
- 🚀 **One-Click Copy**: Copy generated bids instantly to clipboard
- 📱 **Fully Responsive**: Optimized for desktop, tablet, and mobile (even 360px screens!)

## 🏗️ Project Structure

```
ai_chatbot/
├── backend/
│   ├── main.py                    # FastAPI server
│   └── requirements.txt           # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── BidGenerator.jsx  # Main UI component
│   │   │   └── BidGenerator.css  # Styles
│   │   ├── App.jsx
│   │   └── App.css
│   └── package.json
├── src/
│   ├── core/
│   │   ├── llm_client.py         # LLM integration (OpenAI/Anthropic)
│   │   └── config.py             # Configuration management
│   └── agents/
│       ├── bid_generator.py       # Main bid generation logic
│       ├── analyzer.py            # Project description analyzer
│       └── optimizer.py           # Bid optimization strategies
├── setup.sh                       # Automated setup script
├── start.sh                       # Start both frontend & backend
├── .env.example                   # Environment variables template
└── README.md
```

## 🚀 Quick Start

### Automated Setup (Recommended)

```bash
# Make scripts executable
chmod +x setup.sh start.sh

# Run setup (one time only)
./setup.sh

# Get your FREE Gemini API key from: https://makersuite.google.com/app/apikey
# Configure your API key
nano .env  # or use any text editor

# Start the application
./start.sh
```

The app will open at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📖 How to Use

### Smart Mode (Recommended - Zero Effort!)

1. **Copy entire project page** from Freelancer/Upwork
2. **Paste everything** into the textarea
3. **Click "Preview Extraction"** to see extracted details (budget, bids, client info)
4. **Watch the extraction process** in real-time (6 steps with animations!)
5. **Click "Generate Bid"** - done! 🎉

The system automatically extracts:
- 💰 Budget range
- 📊 Number of bids
- 📍 Client location
- ⏰ Time remaining
- 📝 Project description
- Everything else needed!

### Manual Mode (For Custom Control)

- **Project Name**: Copy from the freelance platform
- **Project Description**: Paste the full project description
- **Optional Fields**: Add bid rank, total bids, and pricing for better optimization

### Review Results

The app will show:
- ✅ **Generated Bid**: Professional bid text ready to copy
- 📊 **Project Analysis**: Type, skills required, complexity
- 🎯 **Skill Matching**: Which of your skills match the project
- 💡 **Optimization Tips**: Suggestions to improve win rate
- 📈 **Win Probability**: Estimated chance of winning

### Copy and Submit

Click "📋 Copy" and paste the bid into your freelance platform!

## 🤖 AI Provider Options

### Google Gemini (Default - FREE!)
**✅ Recommended for everyone**
- 🆓 **100% FREE** - No credit card required
- ⚡ Fast and powerful (gemini-2.0-flash-exp)
- 🎯 Great for bid generation
- Get your key: https://makersuite.google.com/app/apikey

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
```

### OpenAI GPT-4 (Paid Alternative)
- 💰 Requires paid API key
- Most powerful option
- Good for complex projects

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_key_here
```

### Anthropic Claude (Paid Alternative)
- 💰 Requires paid API key
- Excellent reasoning
- Good for detailed analysis

```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
```

## 📱 Responsive Design

Fully optimized for all screen sizes:
- 🖥️ **Desktop**: Full-width, multi-column layouts
- 💻 **Laptop**: 1024px+ screens
- 📱 **Tablet**: 768px - 1024px
- 📱 **Mobile**: 480px - 768px
- 📱 **Small Mobile**: 360px - 480px
- 📱 **Extra Small**: Even 360px screens!

## Configuration

Edit [.env](.env) file:

```bash
# Choose AI provider
AI_PROVIDER=openai  # or anthropic

# Add your API key
OPENAI_API_KEY=sk-...

# Customize your profile
YOUR_NAME=Your Name
YOUR_GITHUB=https://github.com/yourusername
YOUR_SKILLS=Python,JavaScript,AI,ML
```

## 🧠 How It Works

### 1. **Project Analysis**
The AI analyzes the project description to extract:
- Project type and complexity
- Required skills and technologies  
- Key requirements and deliverables
- Estimated budget range

### 2. **Skill Matching**
Compares your skills (from config) with project requirements:
- Calculates skill match percentage
- Identifies your relevant experience
- Determines confidence score

### 3. **Bid Generation**
Creates a personalized, professional bid:
- Tailored to specific project requirements
- Includes relevant sample work
- Professional but approachable tone
- Optimal length (100-250 words)

##💡 Tips for Winning Bids

Based on analysis of winning vs. losing bids:

### ✅ DO:
- ✓ Keep bids **concise** (3-5 short paragraphs)
- ✓ Include **sample work** or demo links when relevant
- ✓ State **specific delivery timeline**
- ✓ Show **confidence** without overselling
- ✓ Mention **immediate availability**
- ✓ Address the client's **specific requirements**
- ✓ Use **concrete examples** from your experience

### ❌ DON'T:
- ✗ Write overly long proposals (>300 words)
- ✗ Apply to projects **outside your expertise**
- ✗ Use **generic templates** without customization
- ✗ Ignore specific tools/requirements mentioned
- ✗ Under-price significantly (damages credibility)
- ✗ Make promises you can't deliver

## 🐛 Troubleshooting

**"LLM client not configured" error:**
- Check that your `.env` file exists in the root directory
- Verify your API key is correct
- Make sure `AI_PROVIDER` matches your key (openai or anthropic)

**Frontend can't connect to backend:**
- Ensure backend is running on port 8000
- Check for CORS errors in browser console
- Verify both services are running

**"Module not found" errors:**
- Backend: Make sure you ran `pip install -r backend/requirements.txt`
- Frontend: Make sure you ran `npm install` in the frontend directory

## 📝 License

MIT License - feel free to customize for your needs.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

---

**Built with curiosity by Vicky Kumar**
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Add to `.env` as `OPENAI_API_KEY`

**Anthropic (Alternative)**:
1. Go to https://console.anthropic.com/
2. Generate an API key
3. Add to `.env` as `ANTHROPIC_API_KEY Tips for Winning Bids

Based on analysis of My winning vs. losing bids:

✅ **DO:**
- Keep bids concise (3-5 short paragraphs)
- Provide sample work or demo links
- State specific delivery timeline
- Show confidence without overselling
- Mention immediate availability

❌ **DON'T:**
- Write overly long proposals
- Apply to projects outside your expertise
- Use generic templates without customization
- Ignore the client's specific requirements
- Under-price significantly (damages credibility)

## Future Enhancements

-  Real-time Upwork/Freelancer integration
-  A/B testing different bid strategies
-  Automatic bid success tracking
-  Multi-language support
-  Budget recommendation engine

## License

MIT License - feel free to customize for your needs.
