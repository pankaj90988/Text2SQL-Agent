import os
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from database import DatabaseManager
from sql_chain import SQLGeneratorChain
import pandas as pd

#Load environment variables from .env file
load_dotenv()

st.set_page_config(page_title="Text2SQL Agent - Natural Language to PostgreSQL", page_icon=":icon:", layout="wide")
st.title("🤖Text2SQL Agent")
st.caption("Self-Correcting Text-to-SQL Engine powered by 🔗 LangChain,⚡Groq (Llama 3.3) and 🐘 Neon PostgreSQL DB")


#Read server-level environment configurations
SYSTEM_GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DEFAULT_DB_URL = os.getenv("DATABASE_URL", "")

#Ensure Groq API Key exists in .env
if not SYSTEM_GROQ_API_KEY:
    st.error("❌ System Error: Groq API Key is missing from .env file.")
    st.stop()


#======================================
#Sidebar Setup & Usage Instructions
#======================================
with st.sidebar:
    st.header("⚙️ Database Connection")
    
    # Informational guide card for app users
    st.info(
        "💡 **How to use this App:**\n"
        "1. **Default Mode:** Connects automatically to Pankaj's pre-configured Neon database.\n"
        "2. **Custom Mode:** Expand below to paste your own Neon/PostgreSQL connection string."
    )
    
    # Expander for optional user database URL override
    with st.expander("🛠️ Connect Your Own Database (Optional)", expanded=False):
        custom_db_url = st.text_input(
            "Neon / PostgreSQL Connection String:",
            type="password",
            placeholder="postgresql://user:pass@ep-xyz.neon.tech/neondb?sslmode=require",
            help="Paste a valid PostgreSQL URL. If left empty, default DB will be used."
        )

    # Smart fallback logic: User input > Default .env DB
    active_db_url = custom_db_url.strip() if custom_db_url.strip() else DEFAULT_DB_URL

    st.divider()
    st.subheader("📊 Active Database Schema")

    if not active_db_url:
        st.error("❌ No database URL provided in .env or custom input.")
        st.stop()

    # Render database status badges
    if custom_db_url.strip():
        st.warning("🔗 Connected to: **Custom User Database**")
    else:
        st.success("⚡ Connected to: **Default Sample Database**")

    #Connect and render active schema in sidebar
    try:
        db_manager = DatabaseManager(active_db_url)
        schema = db_manager.get_schema()
        st.text("Tables Schema")
        st.code(schema, language="sql")
    except Exception as err:
        st.error(f"DB Connection Error: {str(err)}")
        st.stop()

#Main Page Query Interface
st.markdown("### 💬 Ask a Question")
st.caption("Enter a question related to the active database schema shown on the left sidebar.")

user_question = st.text_input(
    "Query Prompt:",
    placeholder="e.g., What are the top 3 item or product categories by total sales volume?"
)

run_button = st.button("Get Output", type="primary")

if run_button:
    if not user_question.strip():
        st.toast("Please type a question to analyze.",icon="⚠️")
    else:
        with st.spinner("Analyzing schema, generating query & executing on PostgreSQL..."):
            try:
                # Initialize SQL Generator using system Groq key
                chain = SQLGeneratorChain()
        
                # Execute self-correcting query pipeline
                df, final_query, logs = chain.run_with_self_correction(
                    user_question=user_question,
                    db_manager=db_manager,
                    max_retries=3
                )

                st.success("Query Executed Successfully!")

                # Comment: Display generated PostgreSQL query
                st.subheader("Generated PostgreSQL Query")
                st.code(final_query, language="sql")

                # Comment: Display tabular data results
                st.subheader("Query Results")
                st.dataframe(df, use_container_width=True)

                # Comment: Generate automatic chart if numerical and text columns are present
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                text_cols = df.select_dtypes(include=['object']).columns.tolist()

                if len(text_cols) >= 1 and len(numeric_cols) >= 1:
                    st.subheader("📈 Auto Data Visualization")
                    fig = px.bar(
                        df, x=text_cols[0], y=numeric_cols[0], 
                        title=f"{numeric_cols[0].title()} vs {text_cols[0].title()}",
                        template="plotly_white"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Comment: Show detailed debug execution logs inside expander
                with st.expander("🛠️ Execution Logs (Self-Correction Steps)"):
                    for log in logs:
                        st.write(f"**Attempt {log['attempt']}:** Status - `{log['status']}`")
                        st.code(log['query'], language="sql")
                        if log['status'] == "FAILED":
                            st.error(f"PostgreSQL Error: {log['error']}")

            except Exception as e:
                st.error(f"Execution Error: {str(e)}")