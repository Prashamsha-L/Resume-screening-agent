import streamlit as st
import google.generativeai as genai
import PyPDF2
import io
import os
from dotenv import load_dotenv
import re
import smtplib
from email.message import EmailMessage

load_dotenv()
st.set_page_config(page_title="Resume Screening", layout="wide")

def extract_email(resume_text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, resume_text, re.IGNORECASE)
    return emails[0] if emails else None

def extract_pdf_text(uploaded_file):
    uploaded_file.seek(0)
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text.strip()

def send_email(email, score):
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")
    if not EMAIL_USER or not EMAIL_PASS or not email:
        return False
    
    msg = EmailMessage()
    msg['From'] = f"Hiring Team <{EMAIL_USER}>"
    msg['To'] = email
    
    if score >= 80:
        msg['Subject'] = 'Shortlisted - Next Steps | ABC Technologies'
        body = f"""Dear Candidate,

Thank you for applying to ABC Technologies.

We are pleased to inform you that your profile has been shortlisted for the position based on our initial evaluation (Match Score: {score}%).

Instructions:
1. You will receive a call from our recruitment team within 48 hours to schedule your interview
2. Please ensure you are available next week for the interview process
3. Prepare to discuss your relevant experience and technical skills

We look forward to speaking with you soon.

Best regards,
Hiring Team
ABC Technologies"""
    else:
        msg['Subject'] = 'Application Update | ABC Technologies'
        body = f"""Dear Candidate,

Thank you for your application to ABC Technologies.

After careful review of your profile against our current requirements, we have determined it is not a strong match at this time (Match Score: {score}%).

Instructions:
1. Please consider other suitable positions on our careers page
2. Update your profile and reapply when you gain relevant experience
3. We encourage you to continue building skills in required technologies

We wish you success in your career search.

Best regards,
Hiring Team
ABC Technologies"""
    
    msg.set_content(body)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        return True
    except:
        return False

def get_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("Add GEMINI_API_KEY to .env file")
        st.stop()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

def analyze_resume(model, job_desc, resume_text):
    prompt = f"""Score resume 0-100% vs job:
JOB: {job_desc[:1000]}
RESUME: {resume_text[:2000]}

Format exactly:
SCORE: XX%
STRENGTHS: bullet points
MISSING: bullet points"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "SCORE: 0%\nSTRENGTHS:\nMISSING:"

def parse_result(text):
    st.write("📄 DEBUG - Raw text:", text[:300] + "...")  # REMOVE after fix
    
    # Fix score extraction - case insensitive
    score_match = re.search(r'score[:\s]*(\d+)', text, re.IGNORECASE)
    score = int(score_match.group(1)) if score_match else 0
    
    # Fix strengths extraction
    strengths_match = re.search(r'strengths?[:\s]*([\s\S]*?)(?=\n?missing|$)'
                               , text, re.IGNORECASE)
    strengths = []
    if strengths_match:
        for line in strengths_match.group(1).split('\n'):
            clean = re.sub(r'[*•‣▪▸▹►▬\-\—★☆✦✧●◉◎]+', '', line.strip())
            clean = re.sub(r'\s+', ' ', clean).strip(' :;-')
            if len(clean) > 5:
                strengths.append(clean)
    
    # Fix gaps extraction  
    gaps_match = re.search(r'missing[:\s]*([\s\S]*?)$', text, re.IGNORECASE)
    gaps = []
    if gaps_match:
        for line in gaps_match.group(1).split('\n'):
            clean = re.sub(r'[*•‣▪▸▹►▬\-\—★☆✦✧●◉◎]+', '', line.strip())
            clean = re.sub(r'\s+', ' ', clean).strip(' :;-')
            if len(clean) > 5:
                gaps.append(clean)
    
    st.write(f"✅ DEBUG - Parsed: Score={score}, Strengths={len(strengths)}")  # REMOVE after fix
    
    return {"score": score, "strengths": strengths[:3], "gaps": gaps[:3]}


def get_score_text(score):
    if score >= 90: return "Excellent Match"
    elif score >= 80: return "Strong Match" 
    elif score >= 70: return "Good Match"
    elif score >= 60: return "Fair Match"
    else: return "Poor Match"


st.markdown("""
<div style='
    background: linear-gradient(90deg, #1e40af, #3b82f6);
    color: white;
    padding: 1.5rem;
    text-align: center;
    border-radius: 10px;
    margin-bottom: 2rem;
'>
    <h1 style='margin: 0; font-size: 1.8rem;'>Resume Screening Agent</h1>
    <p style='margin: 0.2rem 0 0 0; font-size: 1rem;'>AI Based Resume Evaluation</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="small")

with col1:
    st.markdown("""
    <div style='margin-bottom: 0.1rem;'>
        <h3 style='color: #1e293b; margin: 0; font-size: 1.4rem;'>Job Description</h3>
    </div>
    """, unsafe_allow_html=True)
    job_desc = st.text_area("", height=250, label_visibility="collapsed", 
                           placeholder="Enter complete job description including required skills, experience, qualifications...")

with col2:
    st.markdown("""
    <div style='margin-bottom: 0.1rem;'>
        <h3 style='color: #1e293b; margin: 0; font-size: 1.4rem;'>Upload Resumes</h3>
    </div>
    """, unsafe_allow_html=True)
    files = st.file_uploader("", type="pdf", accept_multiple_files=True, label_visibility="collapsed")

# Screen Resume button
col1, col2, col3 = st.columns([2,1,2])
with col2:
    st.markdown("""
<style>
.stButton > button {
     background: linear-gradient(90deg, #1e40af, #3b82f6) !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 20px !important;
    padding: 0.8rem 2.5rem !important;
    display: block !important;
    margin: 0 auto !important;
    width: fit-content !important;
    box-shadow: 0 8px 25px rgba(30,64,175,0.3) !important;    
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 35px rgba(30,64,175,0.5) !important;
}
.stButton {
    display: flex !important;
    justify-content: center !important;
}
</style>
""", unsafe_allow_html=True)

if st.button("Screen Resumes",type="primary", use_container_width=True):

        if not job_desc.strip():
            st.error("Enter job description")
        elif not files:
            st.error("Upload resumes")
        else:
            with st.spinner("Analyzing..."):
                model = get_model()
                results = []
                
                bar = st.progress(0)
                for i, file in enumerate(files):
                    text = extract_pdf_text(file)
                    email = extract_email(text)
                    analysis = analyze_resume(model, job_desc, text)
                    parsed = parse_result(analysis)
                    
                    results.append({
                        "file": file.name,
                        "email": email,
                        "score": parsed["score"],
                        "strengths": parsed["strengths"],
                        "gaps": parsed["gaps"],
                        "sent": False
                    })
                    bar.progress((i+1)/len(files))
                
                results.sort(key=lambda x: x["score"], reverse=True)
                st.session_state.results = results
                st.success(f"Complete! {len(results)} resumes analyzed")
                st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)
                st.rerun()


if st.session_state.get("results"):
    st.markdown("---")
    st.markdown("<h2 style='color: #1e293b; text-align: center; margin-bottom: 2rem;'>Screening Results</h2>", unsafe_allow_html=True)
    
    for result in st.session_state.results:
        score = result["score"]
        score_text = get_score_text(score)
        email = result["email"] or "No email found"
        
        # Percentage and status
        color_map = {90: "#10b981", 80: "#f59e0b", 70: "#fbbf24", 60: "#ef4444", 0: "#dc2626"}
        color = color_map.get(max([k for k in color_map if score >= k], default=0))
        
        st.markdown(f"""
        <div style='
            display: flex;
            justify-content: center;
            margin-bottom: 1.5rem;
        '>
            <div style='
                background: linear-gradient(135deg, {color}20, {color}40);
                border: 3px solid {color};
                border-radius: 20px;
                padding: 2rem 2.5rem;
                text-align: center;
                max-width: 300px;
                box-shadow: 0 15px 40px {color}20;
            '>
                <div style='font-size: 3.2rem; font-weight: 800; color: {color}; margin-bottom: 0.5rem;'>
                    {score}<span style='font-size: 1.4rem;'>%</span>
                </div>
                <div style='font-size: 1.1rem; color: {color}; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px;'>
                    {score_text}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
       # Candidate Email address
        st.markdown(f"""
        <div style='
            text-align: center;
            margin-bottom: 1.5rem;
            padding: 1rem 2rem;
            background: rgba(0,155,255,0.8);
            border-radius: 12px;
            border-left: 5px solid {color};
            max-width: 500px;
            margin-left: auto;
            margin-right: auto;
            font-family: monospace;
            font-size: 1rem;
            font-weight: 500;
            color: #1e293b;
            word-break: break-all;
        '>
             {email}
        </div>
        """, unsafe_allow_html=True)
        
        # Send Email button for both Shortlisted and rejected resumes
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
        with col_btn2:
            if result["email"] and not result["sent"]:
                action = "Shortlist" if score >= 80 else "Reject"
                if st.button(f"Send {action} Email", key=f"email_{result['file']}", 
                           use_container_width=True, type="primary"):
                    if send_email(result["email"], score):
                        result["sent"] = True
                        st.session_state.results = st.session_state.results
                        st.success("Email sent successfully!")
                        st.rerun()
            elif result["sent"]:
                st.success("Email Sent")
            else:
                st.info("No email found")
        
        
        st.markdown("---")
        
        col_strength, col_gap = st.columns(2)
        
        with col_strength:
            st.markdown(f"<h4 style='color: #10b981; margin-bottom: 0.8rem;'>Strengths</h4>", unsafe_allow_html=True)
            if result["strengths"]:
                for strength in result["strengths"][:3]:
                    st.success(strength)
            else:
                st.info("No strengths identified")
        
        with col_gap:
            st.markdown(f"<h4 style='color: #ef4444; margin-bottom: 0.8rem;'>Skill Gaps</h4>", unsafe_allow_html=True)
            if result["gaps"]:
                for gap in result["gaps"][:3]:
                    st.warning(gap)
            else:
                st.info("No gaps identified")


