# 📊 WhatsApp Chat Analyzer

A simple and efficient **WhatsApp Chat Analyzer** built using Python and Streamlit. This project focuses on extracting insights and statistics from exported WhatsApp chat data **without any AI/LLM integration**.

---

## 🚀 Features

* 📈 **Basic Statistics**

  * Total messages
  * Total words
  * Media shared
  * Links shared

* 👤 **User-wise Analysis**

  * Most active users
  * Message contribution distribution

* 📅 **Timeline Analysis**

  * Daily timeline
  * Monthly timeline

* 🔥 **Activity Maps**

  * Most busy day
  * Most busy month
  * Weekly activity heatmap

* ☁️ **Word Analysis**

  * WordCloud generation
  * Most common words
  * Stopwords removal (including Hinglish support)

* 🔗 **Link Extraction**

  * Count and analyze shared links

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python
* **Libraries Used:**

  * pandas
  * matplotlib
  * seaborn
  * wordcloud
  * urlextract

---

## 📁 Project Structure

```
.
├── app.py              # Main Streamlit application
├── helper.py           # Analysis functions
├── preprocessor.py     # Chat preprocessing logic
├── stop_hinglish.txt   # Custom stopwords
├── requirements.txt    # Dependencies
├── setup.sh            # Setup script (optional)
└── .gitignore
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/VedantKawade3/Whatsapp-chat-analyser.git
cd whatsapp-chat-analyser
```

### 2. Create virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

### 1. Export WhatsApp Chat

* Open WhatsApp
* Go to chat → Click on **3 dots → More → Export Chat**
* Choose **Without Media**
* Save `.txt` file

### 2. Run the app

```bash
streamlit run app.py
```

### 3. Upload chat file in UI

* Open browser (usually `http://localhost:8501`)
* Upload exported `.txt` file
* Select user (or overall analysis)
* Explore insights

---

## 🔍 How It Works

1. **Preprocessing (`preprocessor.py`)**

   * Converts raw chat text into structured DataFrame
   * Extracts:

     * Date
     * User
     * Message

2. **Helper Functions (`helper.py`)**

   * Perform statistical analysis
   * Generate plots and word clouds

3. **Streamlit UI (`app.py`)**

   * Handles user interaction
   * Displays visualizations

---

## ⚠️ Limitations

* Works only with **exported WhatsApp `.txt` format**
* No support for:

  * Emojis analysis (basic version)
  * Sentiment analysis
* Hinglish handling depends on custom stopwords file

---

## 🤝 Contributing

Feel free to fork this project and improve it. Pull requests are welcome.

---

## 📜 License

This project is open-source and available under the MIT License.

---

## 👨‍💻 Author

Developed as part of a learning project to understand:

* Data preprocessing
* Exploratory data analysis
* Streamlit app development

---
