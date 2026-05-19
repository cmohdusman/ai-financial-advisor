# 💰 AI Financial Advisor

An AI-powered financial advisor built using **CrewAI, FastAPI, and Streamlit**.  
This application analyzes transaction data, evaluates financial risk, and provides personalized financial insights, advice, and Q&A support.

---

## 🚀 Features

- 📊 Transaction analysis & expense categorization  
- ⚠️ Risk profiling (Conservative / Moderate / Aggressive)  
- 💡 Personalized financial recommendations  
- 💬 AI-powered financial Q&A assistant  
- 📈 Interactive dashboard  

---

## 📁 Project Structure

```
ai-financial-advisor/
│
├── backend/              # FastAPI backend APIs
├── frontend/             # Streamlit UI
├── agents/               # CrewAI agents & YAML config
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
└── README.md
```

---

## 🔧 Setup Instructions

### ✅ 1. Create Virtual Environment

```bash
python -m venv myenv
```

#### ▶ Activate (Windows)

```bash
myenv\Scripts\activate
```

#### ▶ Activate (Mac/Linux)

```bash
source myenv/bin/activate
```

---

### ✅ 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### ✅ 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_api_key
OPENAI_MODEL_NAME=gpt-4o-mini
OPENAI_TEMPERATURE=0.2
```

---

## ⚙️ Run the Application

### ▶ Start Backend (FastAPI + CrewAI)

```bash
uvicorn backend.main:app --reload
```

Backend will be available at:

```
http://localhost:8000
```

---

### ▶ Start Frontend (Streamlit UI)

```bash
streamlit run frontend/app.py
```

Application will open at:

```
http://localhost:8501
```

---

## 🧠 Tech Stack

- **CrewAI** – Multi-agent orchestration  
- **FastAPI** – Backend APIs  
- **Streamlit** – UI/dashboard  
- **OpenAI / LLMs** – AI processing  
- **Python** – Core language  

---

## ✅ Usage Flow

1. Upload a transaction CSV file  
2. AI processes and categorizes spending  
3. System calculates financial risk profile  
4. Generates insights and recommendations  
5. Ask financial questions via AI assistant  

---

## 📄 Example CSV Format

```
date,amount,merchant
2025-05-01,-5000,Rent
2025-05-03,-1200,Groceries
2025-05-05,-2000,Insurance
```

---

## ⚠️ Important Notes

- Backend must be running before starting Streamlit  
- Use Python **3.10+ recommended**  
- Ensure `.env` file is properly configured  
- CrewAI depends on correct YAML configuration  

---

## 🧪 Debug Tips

- Verify config loading:
  ```python
  print(config["tasks"].keys())
  ```

- Enable verbose logging:
  ```python
  verbose=True
  ```

- Check backend logs for missing tasks or execution failures  

---

## 🐳 (Optional) Docker Setup

Create a `Dockerfile`:

```dockerfile
FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---


