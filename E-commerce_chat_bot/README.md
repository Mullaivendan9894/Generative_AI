[![GitHub repo](https://img.shields.io/badge/E_commerce-Chat_bot-blue?logo=github)](https://github.com/Mullaivendan9894/Generative_AI/tree/master/E-commerce_chat_bot)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-ff4b4b?logo=streamlit&logoColor=white)](https://generativeai-e-com-chat-bot.streamlit.app/)

# E-commerce Chatbot 🤖

An intelligent chatbot for e-commerce support, built with Streamlit and Groq API.
![app_screenshot.png](https://github.com/Mullaivendan9894/Generative_AI/blob/master/E-commerce_chat_bot/app_screenshot.png)

### 1. Features

- **FAQ Handling**: Answers common questions using semantic search
- **Product Queries**: SQL-based product search and recommendations
- **Small Talk**: Natural conversation capabilities
- **Smart Routing**: Automatically routes queries to the appropriate handler

### 2. How It Works 🛠️

The chatbot uses a sophisticated pipeline to intelligently process user queries. Here's the step-by-step flow:

1.  **Query Input:** A user submits a question through the Streamlit web interface.

2.  **Semantic Routing:**
    *   The query is first analyzed by a **Semantic Router**.
    *   This lightweight model classifies the user's intent into one of three categories without needing a large LLM, ensuring fast and efficient routing:
        *   **`FAQ Intent`**: For questions about shipping, returns, policies, etc.
        *   **`Product Intent`**: For queries about products, prices, or recommendations.
        *   **`Small Talk Intent`**: For greetings and casual conversation.

3.  **Intent-Specific Processing:**
    *   **For FAQ Queries (RAG):**
        *   The query is sent to a **ChromaDB vector database**.
        *   A similarity search finds the most relevant FAQ from pre-processed documents.
        *   This context is passed to the LLaMA 3.3 LLM via Groq to generate a natural language answer.
    *   **For Product Queries:**
        *   The query is sent to a **SQL Query Generator** (a dedicated LLM function) to create a precise SQL command.
        *   This SQL query is executed on an **SQLite database** containing product information.
        *   The retrieved product data is sent to the main LLM to be formatted into a friendly, numbered list for the user.
    *   **For Small Talk:**
        *   The query is handled by a dedicated module designed to engage in friendly, natural conversation.

4.  **Response Generation:** The final response is sent back to the Streamlit UI and displayed to the user.

### 3. Architecture Overview

The system leverages a powerful tech stack to make this possible:

*   **Frontend:** Streamlit
*   **LLM & Inference:** LLaMA 3.3 via Groq API (for high speed)
*   **Query Routing:** Semantic Router
*   **FAQ Database:** ChromaDB (Vector Database)
*   **Product Database:** SQLite
*   **Language:** Python

### 4. Project Links 🔗

*   **Live Demo:** [Experience the Chatbot](https://generativeai-e-com-chat-bot.streamlit.app/) 
*   **LinkedIn Post:** [See my project post on LinkedIn](https://www.linkedin.com/feed/update/urn:li:activity:7208943790845571072/)
*   **GitHub Repository:** [Source Code](https://github.com/Mullaivendan9894/Generative_AI/tree/master/E-commerce_chat_bot)

### 5. Setup

1.  Clone the repository:
    <pre>
    git clone https://github.com/your-username/ecommerce-chatbot.git
    cd ecommerce-chatbot
    </pre>

2.  Install dependencies:
    <pre>
    pip install -r requirements.txt
    </pre>

3.  Set up environment variables:
    Create `.streamlit/secrets.toml`:
    <pre>
    GROQ_API_KEY = "your_groq_api_key_here"
    GROQ_MODEL = "llama-3.3-70b-versatile"
    </pre>

4.  Run the app:
    <pre>
    streamlit run app.py
    </pre>

### 6. File Structure
<pre>
ecommerce-chatbot/
├── .streamlit/
│ └── secrets.toml
├── resources/
│ ├── faq_data.csv
│ └── product.db
├── app.py
├── faq_handling.py
├── query_router.py
├── small_talk_handle.py
├── sql_handling.py
├── requirements.txt
└── README.md </pre>

