# 🤖 AI-Powered Autonomous Self-Correcting Text-to-SQL Agent

An advanced Generative AI application built with **Streamlit**, **LangChain**, and **Groq (Llama 3.3 70B)** that translates natural language questions into complex, production-grade PostgreSQL queries. The system features an autonomous, multi-turn feedback loop that automatically captures database compilation errors and rewrites queries in real-time.

---

## 🌟 Key Technical Features

* **Agentic Self-Correction Loop:** Uses an automated feedback loop (`max_retries=3`). If the initial AI-generated SQL query fails on the database, the system catches the error message, re-prompts the LLM with structural context, and auto-heals the query dynamically.
* **Dynamic Schema Extraction:** Zero hardcoding. The app queries PostgreSQL's `information_schema.columns` catalog at runtime to dynamically inject the active database structure into the LLM context window.
* **Strict Security Guardrails:** Includes a built-in prevention layer that scans queries at runtime and intercepts/blocks dangerous DDL/DML keywords (`DROP`, `DELETE`, `UPDATE`, `ALTER`, etc.) to mitigate SQL Injection risks.
* **Type-Driven Auto-Visualization:** Automatically analyzes the returned Pandas DataFrame data types. If text (categorical) and numerical columns are detected, it builds interactive charts instantly using **Plotly Express**.
* **Transparent Multi-Turn Logs:** Built an interactive debugging workspace inside Streamlit using `st.expander` to display granular, step-by-step logs of every execution attempt and compiler error.

---

## 🛠️ System Architecture Flow

1. **User Query:** User enters an English question in the Streamlit UI.
2. **Schema Injection:** `DatabaseManager` pulls the live schema from the Neon PostgreSQL database.
3. **SQL Generation:** LangChain sends the question + schema context to `Llama-3.3-70b-versatile` (with deterministic `temperature=0.0`).
4. **Execution Check:** The app validates query security. If safe, it executes the query via `psycopg2`.
5. **Self-Correction (If Fails):** If the DB throws a syntax or column error, the error traceback is routed back into the LLM chain to regenerate a corrected query.
6. **Output Delivery:** Displays the final verified SQL code, interactive data table (Pandas), and automated Plotly visualizations.

---

## 📦 Project Directory Structure

```text
├── app.py                  # Streamlit Main Dashboard & Interface
├── database.py             # DatabaseManager (Schema extraction & Security check)
├── sql_chain.py            # SQLGeneratorChain (LangChain LLM setup & Auto-correction loop)
├── config.py               # Prompt templates (SQL_GENERATION_PROMPT, SQL_CORRECTION_PROMPT)
├── requirements.txt        # Third-party Python dependencies
└── .gitignore              # Hides local env keys, __pycache__, and venv/
```

---

## 🚀 Installation & Local Setup

### 1. Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
streamlit run app.py
```

---

## 🧰 Tech Stack Used

* **Frontend:** Streamlit
* **AI Framework:** LangChain (Core & Groq Wrapper)
* **LLM Engine:** Llama-3.3-70b-versatile (via Groq API Cloud)
* **Database Driver:** Psycopg2-binary
* **Cloud Database:** Neon PostgreSQL
* **Data Processing & Viz:** Pandas, Plotly Express
