from dotenv import load_dotenv
import PyPDF2
import streamlit as st
from openai import OpenAI
import os # To use .env variables
import io # To Stream the data using RAM, without needing hard drive files
load_dotenv()
st.set_page_config(page_title="AI Resume Critiquer", page_icon="📝", layout="centered")

st.title("AI Resume Critiquer")
st.markdown("If you send me your resume, I can help to suggest feedbacks and improvements!")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

uploaded_file = st.file_uploader("Please upload your resume in PDF/txt format",type=["PDF","txt"])
expected_job = st.text_input("What job or type of job are you looking for?")

inspect = st.button("Inspect your resume") # False before we press the button, True afterwards

def extract_text_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_file(uploaded_file): # Extract text from the uploaded pdf / txt file in order to pass it to the LLM
    if uploaded_file.type == "application/pdf":
        return extract_text_pdf(io.BytesIO(uploaded_file.read()))
    else:
        return uploaded_file.read().decode("utf-8") # Standard txt format

if inspect == True and uploaded_file is not None: # When we have pressed the button and loaded the CV, display the following
    # st.write("Inspecting resume...")
    try:
        file_content = extract_text_file(uploaded_file)

        if file_content.strip() is None:
            st.error("The file uploaded does not have any content.")
            st.stop()
        else:
            prompt = f"""Make constructive feedback about the CV document that I joined.
            Make sure:
                1 - You are clear and simple in your remarks
                2 - You evaluate the overall aspect of the CV (how it looks, how it's field, the structure)
                3 - You analyze interesting points and weak points related to {expected_job if not None else "all jobs"}
                
            Resume content: 
            
            {file_content}

            Feel free to add any suggestion that you find insightful for the resume attached"""

            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model = "gpt-4.1",
                messages=[
                    {"role":"system","content": "You are an HR / HRBP expert and you perfectly know how to review resumes for job applications"}, # "role":"system" gives context to the LLM without answer from it
                    {"role":"user","content":prompt}
                ],
                temperature = 0.7, # lowest randomness
                max_tokens=500
            )
            st.markdown("### Results:")
            st.markdown(response.choices[0].message.content)
    
    except Exception as e:
        st.error(f"Error occured: {str(e)}")