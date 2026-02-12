import streamlit as st
import PyPDF2
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up the Streamlit page config
st.set_page_config(page_title="AI Resume Critique", layout="wide")
st.title("🧠 AI Resume Critique Bot")
st.write("Upload your resume (PDF) and optionally include a job description for tailored feedback.")

# Help/FAQ section in the sidebar
st.sidebar.header("❓ Need Help?")
st.sidebar.write("Here are some tips on how to get the best out of the AI feedback:")
st.sidebar.markdown("""
-  **Upload a detailed resume** for better suggestions.
-  **Paste a job description** to get more accurate matching.
-  **Choose a tone** that suits your feedback style (Strict HR or Friendly Mentor).
-  The AI will analyze your resume and offer smart, tailored recommendations.
""")

# Upload Resume PDF
uploaded_file = st.file_uploader("📄 Upload your resume (PDF only)", type="pdf")

# Function to extract text from the PDF
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted
    return text

# Extract resume text
resume_text = ""
if uploaded_file:
    with st.spinner("Extracting text from your resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
        if resume_text.strip() == "":
            st.warning("The resume is empty or unreadable. Please upload a different file.")
        else:
            st.subheader("📄 Resume Text")
            st.text_area("Extracted Resume Text", resume_text, height=300)

# Job Description Input
st.subheader("📝 Job Description (Optional)")
job_description = st.text_area("Paste the job description here to get more targeted feedback.", height=200)

# Feedback Tone Selection
st.subheader("🎯 Select Feedback Tone")
tone = st.selectbox("Choose tone for feedback", ["Strict HR", "Friendly Mentor"])

# Button to generate feedback
if st.button("Generate AI Feedback"):
    if resume_text.strip() == "":
        st.warning("Resume text is empty! Please upload a valid resume.")
    else:
        with st.spinner("Generating feedback using LLaMA 3..."):
            GROQ_API_KEY = os.getenv("GROQ_API_KEY")
            if not GROQ_API_KEY:
                st.error("Missing GROQ_API_KEY in environment. Please set it in your .env file.")
            else:
                # Construct the user message with enhancements
                user_message = f"""
Here is a resume:

{resume_text}

"""

                if job_description.strip():
                    user_message += f"""
This is the job description it is intended for:

{job_description}
"""

                user_message += f"""
Please provide a structured response that includes the following:

1. Suggestions for improving the resume in a {tone.lower()} tone.
2. A comparison of the resume against the job description — especially key skills and keywords.
3. List of **matched** and **missing** keywords or skills.
4. A **rating score (out of 10)** for how well the resume matches the job description.
5. Overall final recommendations.

Format the feedback clearly under separate headings.
"""

                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "messages": [
                        {
                            "role": "system",
                            "content": f"You are an expert resume reviewer giving {tone.lower()} feedback."
                        },
                        {
                            "role": "user",
                            "content": user_message
                        }
                    ],
                    "model": "llama-3.3-70b-versatile"
                }

                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload
                )

                if response.status_code == 200:
                    result = response.json()
                    ai_feedback = result["choices"][0]["message"]["content"]

                    st.subheader("💡 AI Feedback")
                    st.markdown(ai_feedback)

                    st.download_button("Download Feedback", ai_feedback, file_name="ai_feedback.txt")
                else:
                    st.error("❌ Failed to get feedback from LLaMA 3. Please try again later.")
