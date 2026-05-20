from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
import io
import base64

from PIL import Image
import pdf2image
import google.generativeai as genai


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(user_input,pdf_content,prompt):
    model = genai.GenerativeModel("gemini-2.5-flash")
    enhanced_prompt = f"{prompt}\n\nIMPORTANT: Provide a brief, accurate, and concise response. Avoid lengthy explanations. Be direct and to the point."
    response=model.generate_content([enhanced_prompt,pdf_content[0],user_input])
    return response.text


def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        ## Convert the PDF to image
        images=pdf2image.convert_from_bytes(uploaded_file.read())

        first_page=images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")
    

## Streamlit App

st.set_page_config(page_title="ATS Resume Expert")
st.markdown("<h1 style='text-align: center;'>ATS Tracking System</h1>", unsafe_allow_html=True)

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

input_text=st.text_area("Job Description: ",key="input")
uploaded_file=st.file_uploader("Upload your resume(PDF)",type=["pdf"])


if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

st.divider()

# Display conversation history
st.subheader("Conversation")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Custom prompt input
if uploaded_file  and input_text is not None:
    user_prompt = st.chat_input("Ask anything about your resume...")
    
    if user_prompt:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_prompt)
        
        # Get AI response
        with st.spinner("Analyzing..."):
            pdf_content=input_pdf_setup(uploaded_file)
            response=get_gemini_response(user_prompt, pdf_content, input_text)
            
            # Add assistant message to history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Display assistant message
            with st.chat_message("assistant"):
                st.write(response)
else:
    st.info("Please upload resume and enter job description to start the conversation")
    