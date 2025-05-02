# GenAI-Medical-Policy-Analysis
# 🧠 AI-Powered Medical Policy Analyzer

This project is a **Generative AI-powered document analysis tool** designed to automate the extraction of critical insights from medical policy documents. Developed for healthcare payer organizations, the system enables users to upload policy PDFs and ask natural language questions to receive intelligent, contextual answers.

---

## 🚀 Key Features

- 📄 Upload and analyze multiple medical policy documents (PDF format)
- 🔍 Automatically extract 18 predefined critical data elements
- 🤖 Conversational Q&A powered by **OpenAI GPT models**
- 🧠 Vector-based retrieval using **LangChain**
- ☁️ Cloud-ready (built with AWS integration)
- 🖥️ User-friendly interface built with **Streamlit**

---

## 🏗️ Tech Stack

| Layer       | Technology                      |
|------------|----------------------------------|
| Frontend    | Streamlit                        |
| Backend     | Python, LangChain         |
| AI Engine   | OpenAI (GPT-3.5 / GPT-4 APIs)    |
| PDF Parsing | PyPDF2                           |
| Cloud       | AWS (EC2/S3), Python-dotenv      |
| Database    | MongoDB, Neo4j (evaluated)       |

---

## 📁 Project Structure
```
─ main.py                 # Streamlit entry point
─ app.py                  # Alternative or legacy Streamlit app
─ langchain_helper.py     # Core logic for PDF analysis and Q&A
─ langchain_helper1.py    # Backup/experimental version
─ readfile.py             # PDF text extraction
─ readfile2.py            # Variant PDF reader
─ requirements.txt        # Python dependencies
─ .env                    # OpenAI and AWS credentials (not included)
```
---

## 🚀 Features

- Upload and analyze medical policy documents (PDF format)
- Extract 18 predefined critical data elements
- Ask natural language questions about the policy content
- Uses OpenAI GPT, LangChain for intelligent response
- Runs on Streamlit with a user-friendly UI
- Ready for cloud deployment (e.g., AWS)

---

## 🛠️ Tech Stack

| Component    | Technology         |
|--------------|--------------------|
| Interface    | Streamlit           |
| Backend      | Python              |
| AI Model     | OpenAI GPT-3.5/4    |
| Embedding    | LangChain / OpenAI  |
| PDF Parser   | PyPDF2              |
| Deployment   | AWS (EC2/S3)        |
| Database     | MongoDB, Neo4j (evaluated) |

---

## ⚙️ Setup Instructions

1. Clone the Repository

```bash
git clone https://github.com/your-username/med-policy-insight-ai.git
cd med-policy-insight-ai
```
2. Create a Virtual Environment (Optional)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install Dependencies

```bash
pip install -r requirements.txt
```

4. Add Environment Variables

- Create a .env file in the root directory:
```
OPENAI_API_KEY=your_openai_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
```
🔒 Do not upload .env, .pem, or Git tokens to public repositories.

---

### 🧪 Run the Application

```
streamlit run main.py
```
---

### 👤 Author


**Atharva Devne**  






