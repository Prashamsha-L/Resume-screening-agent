# Resume-screening-agent
Resume Screening Agent is an AI-powered tool that automatically analyzes resumes against job descriptions using machine learning and natural language processing to score candidates (0-100%), identify strengths, and highlight skill gaps.

## Features
- Batch upload & process multiple PDF resumes with progress bar
- Gemini AI scoring (0-100%) with strengths & skill gaps analysis
- Color-coded score cards like Excellent,Strong,Good,Fair,Poor Match
- Automatic email extraction via regex from resume text
- One-click email notifications: Shortlist (≥80%) or Reject emails

## Limitation
- PDF-only support, no DOCX/Word/images/scanned PDFs
- Sequential processing, no parallel Gemini API calls
- No data persistence, results lost on page refresh
- Gmail SMTP only, no Outlook/enterprise email support

## Tech Stack & APIs
- Frontend: Streamlit (wide layout, custom CSS/JS)
- Backend: Python 3.11 
- AI Model: Google Gemini (gemini-2.5-flash)
- PDF Parsing: PyPDF2
- Email: smtplib + Gmail SMTP (port 465)
- Config: python-dotenv (.env)
- Text Processing: re (regex)
- Storage: Streamlit Session State

## Setup & Run Instructions (Windows)
#### 1. Clone/Download repository
git clone <your-repo-url>
cd resume-screening-agent

#### 2. Create virtual environment
python -m venv venv

#### 3. Activate virtual environment
venv\Scripts\activate

#### 4. Install dependencies
pip install -r requirements.txt

#### 5. Run application
streamlit run app.py

## Potential Improvements
- File Support: docx2txt, pytesseract for scanned PDFs/images
- Export: CSV/Excel download with all candidates
- Performance: asyncio for parallel Gemini API calls
