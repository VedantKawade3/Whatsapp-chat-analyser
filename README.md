# 💬 WhatsApp Chat Analyzer + 🧠 AI Insights

A powerful **WhatsApp Chat Analyzer** built using Python and Streamlit that not only extracts statistical insights but also leverages **Google Gemini** to generate **AI-driven personality and communication analysis**.

---

### Live demo: https://whatsapp-chat-analyser-vedant.streamlit.app/
---

## 🚀 Features

### 📊 1. Basic Analytics

* Total messages
* Total words
* Media shared
* Links shared

---

### 👤 2. User-wise Analysis

* Most active users
* Contribution percentage
* Individual user filtering

---

### 📅 3. Timeline Analysis

* Daily message trends
* Monthly activity trends

---

### 🔥 4. Activity Insights

* Most active day of week
* Most active month
* Weekly heatmap (day × time)

---

### ☁️ 5. Text & Word Analysis

* WordCloud generation
* Most common words
* Hinglish + custom stopwords filtering
* Removed noise:

  * deleted messages
  * media placeholders

---

### 🔗 6. Link Analysis

* Total links shared
* URL extraction using regex + parsing

---

### 😂 7. Emoji Analysis

* Emoji frequency table
* Top emoji distribution (pie chart)

---

### 🧠 8. AI-Powered Personality Analysis (NEW 🔥)

Using **Google Gemini**, the system analyzes user chat behavior and provides:

* Communication style
* Tone (formal, casual, humorous, etc.)
* Conversation behavior
* Social personality
* Dominant topics
* Strengths & weaknesses
* Confidence score
* Final personality summary

👉 Works **per user** (not overall) for better accuracy

---

## 🛠️ Tech Stack

### 🖥️ Frontend

* **Streamlit**

### ⚙️ Backend

* Python

### 📦 Libraries Used

* pandas
* matplotlib
* seaborn
* wordcloud
* urlextract
* emoji

### 🤖 AI Integration

* **Google Gemini API**

---

## 📁 Project Structure

```
.
├── app.py                  # Main Streamlit application
├── helper.py               # Analytics functions
├── preprocessor.py         # Chat parsing logic
├── gemini_service.py       # Gemini API integration
├── insights.py             # AI prompt + structured output
├── config.py               # Model configs
├── stop_hinglish.txt       # Custom stopwords
├── requirements.txt        # Dependencies
├── setup.sh                # Setup script (optional)
├── .streamlit/
│   ├── config.toml         # Dark theme config
│   └── secrets.toml        # API keys (production)
└── .gitignore
```

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/VedantKawade3/Whatsapp-chat-analyser.git
cd Whatsapp-chat-analyser
```

---

### 2. Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/Mac
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Gemini API Setup (IMPORTANT)

### 1. Get API Key from:

👉 Google AI Studio

---

### 2. Set Environment Variable

#### Windows:

```bash
set GEMINI_API_KEY=your_api_key
```

#### Linux/Mac:

```bash
export GEMINI_API_KEY=your_api_key
```

---

### 3. (Optional - Production)

Create file:

```
.streamlit/secrets.toml
```

```toml
GEMINI_API_KEY = "your_api_key"
```

---

## ▶️ Usage

### 1. Export WhatsApp Chat

* Open WhatsApp
* Go to chat → **3 dots → More → Export Chat**
* Select **Without Media**
* Save `.txt` file

---

### 2. Run App

```bash
streamlit run app.py
```

---

### 3. Use UI

* Upload `.txt` file
* Select user
* Choose:

  * 📊 **Show Analysis** → Normal analytics
  * 🧠 **AI Analysis** → Gemini insights

---

## 🔍 How It Works

### 1. Preprocessing (`preprocessor.py`)

* Parses raw chat text
* Converts to structured DataFrame
* Extracts:

  * Date
  * User
  * Message
  * Time features

---

### 2. Analytics (`helper.py`)

* Statistical computations
* Word filtering
* Graph generation

---

### 3. AI Insights (`insights.py` + `gemini_service.py`)

* Converts chat → prompt
* Sends to Gemini API
* Returns structured personality analysis

---

### 4. UI (`app.py`)

* Interactive dashboard
* Dual-mode analysis (Normal + AI)

---

## ⚠️ Limitations

* Works only with **WhatsApp exported `.txt` format**
* AI insights depend on:

  * message quantity
  * message quality
* Free tier Gemini API has:

  * rate limits
  * token limits

---

## 🔥 Future Improvements

* Sentiment analysis
* Toxicity detection
* Chat summarization
* Multi-user comparison
* Real-time chat dashboard
* Deployment on cloud (Streamlit Cloud / Vercel backend)

---

## 🤝 Contributing

Pull requests are welcome.
Feel free to fork and enhance features.

---

## 📜 License

MIT License

---

## 👨‍💻 Author

Built to deeply understand:

* Data preprocessing
* Exploratory Data Analysis (EDA)
* Streamlit app architecture
* AI integration using LLMs

---