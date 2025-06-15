# moneymentor

An interactive web platform designed to teach financial concepts through gamified tools and educational content, aimed at users of different age groups.

## Project Description

moneymentor provides a suite of interconnected tools and games to make learning about money engaging and accessible. It features AI-powered assistants for financial planning and advice, along with various simulators and games covering saving, spending, budgeting, and investing.

The project is structured as a collection of static frontends (HTML, CSS, JavaScript) interacting with multiple Python Flask backend microservices.

## Features

*   **AI Financial Chatbot:** Get answers to general financial questions using an AI assistant powered by Groq and backed by a RAG (Retrieval Augmented Generation) system for document-based information.
*   **Goal-Based Investment Planner:** Plan how to save and invest for future goals based on risk profile and target amount, with AI-generated guidance.
*   **AI Tax Strategy Suggester:** Receive general ideas and explanations for Indian income tax saving strategies based on income and age. **(Disclaimer: This is NOT professional tax advice. Always consult a qualified tax professional.)**
*   **Gamified Finnyland:** An interactive section with age-group specific financial learning activities:
    *   **Tiny Savers (Ages 5-8):** Finance Story Teller, Good Deed Reward Checker, Shopkeeper Roleplay, Piggy Bank Simulator.
    *   **Smart Spenders (Ages 9-12):** Dreamboard (Goal Setting), Spin Wheel Financial Quiz, Daily Finance Diary.
    *   **Teen Investors (Ages 13-17):** UPI Simulator (Payment), Virtual Stock Game, Savings vs Investment Planner.

## Architecture

The application consists of:

1.  **Static Frontends:** HTML, CSS, and JavaScript files for each tool and dashboard. These are designed to be served statically (e.g., by opening `index.html` directly in a browser or using a simple web server).
2.  **Backend Microservices:**
    *   `chatbot_server.py`: Flask server for the AI Chatbot (Port 5003).
    *   `goal.py`: Flask server for the Goal Recommendation and Market Context (Port 5002).
    *   `tax_tool_server.py`: Flask server for the AI Tax Suggester (Port 5004).
    *   `app.py`: (Potentially a core backend or older combined service) Flask server running on Port 5000, containing some API routes (`/chatbot`, `/goal`, `/tax`). *Note: The frontend HTML files for Chatbot, Goal, and Tax currently point to ports 5003, 5002, and 5004 respectively, suggesting they use the dedicated servers.*

To run the full application, you need to start all relevant backend servers concurrently.

## Technologies Used

**Frontend:**

*   HTML, CSS, JavaScript
*   Comic-themed styling (`stylesp.css`, `styles.css`, individual CSS files)
*   [Chart.js](https://www.chartjs.org/) for data visualization (Goal Planner, Expense Diary)
*   [Confetti.js](https://www.npmjs.com/package/canvas-confetti) for celebratory effects (Piggy Bank)

**Backend:**

*   [Flask](https://flask.palletsprojects.com/) (Python web framework)
*   [Groq API](https://groq.com/) (for AI Chatbot and Tax Suggester)
*   [Sentence Transformers](https://www.sbert.net/) (for RAG embeddings)
*   [Faiss-CPU](https://github.com/facebookresearch/faiss) (for efficient similarity search in RAG)
*   [PyMuPDF](https://pymupdf.readthedocs.io/) (for PDF processing in RAG)
*   [yfinance](https://pypi.org/project/yfinance/) (for fetching real-time market data in Chatbot)
*   [NewsAPI-Python](https://github.com/mattlisari/newsapi-python) (for fetching financial news in Chatbot)
*   [gunicorn](https://gunicorn.org/) (listed in requirements, typically for production deployment)
*   [python-dotenv](https://pypi.org/project/python-dotenv/) (for loading environment variables)
*   [numpy](https://numpy.org/) (numerical operations)
