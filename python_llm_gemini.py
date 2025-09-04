import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import PyPDF2
import pandas as pd
import tempfile
import os

#Only suitable for running locally when you are inserting your API key in this code only
#Set up google Generative AI API key
#genai.configure(api_key="API key here!")
#model = genai.GenerativeModel("gemini-1.5-flash")

#But in the deployment with stream cloud
import streamlit as st
import google.generativeai as genai
# Correct way: read key from secrets
api_key = st.secrets["GOOGLE_API_KEY"]
# Configure the API
genai.configure(api_key=api_key)
# Create model instance
model = genai.GenerativeModel("gemini-1.5-flash")

#Function: Translate text using Google Generative AI 
def translate_text_gemini(text, target_language):
    try:
        prompt = f"Translate the following text into {target_language}. Provide only the translated response:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error During Translation: {e}"
    
#Function : Extract text from uploaded files
def extract_text_from_file(uploaded_file):
    if uploaded_file.name.endswith('.pdf'):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(uploaded_file.getbuffer())   
            with open(temp_file.name, 'rb')as file:
                reader= PyPDF2.PdfReader(file)
                text=''
                for page in reader.pages:
                    text += page.extract_text() + '\n'
        os.remove(temp_file.name)
        return text
    elif uploaded_file.name.endswith('.txt'):
        return uploaded_file.getvalue().decode("utf-8")
    elif uploaded_file.name.endswith('.csv'):
        df= pd.read_csv(uploaded_file)
        return " ".join(df.astype(str).values.flatten())
    elif uploaded_file.name.endswith('.xlsx'):
        df= pd.read_excel(uploaded_file)
        return " ".join(df.astype(str).values.flatten())

    else:
        return "Unsupported file format. Please upload a PDF or txt, CSV or XLSX file format alone."
    

#Function : Convert text to speech
def text_to_speech(text, language='en'):
    try:
        tts = gTTS(text=text, lang=language)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            tts.save(temp_file.name)
            return temp_file.name
    except Exception as e:
        return f'Error during text-to-speech conversion: {e}'
        
# Streamlit app UI
st.set_page_config(page_title="Google Gemini Translation and Text-to-speech App", page_icon="$%$", layout='wide')
st.title("Google Gemini Translation and Text-to-speech App")
st.write("This app allows you to translate text using Google Gemini and convert it to speech. You can also upload ")

#Text input or file upload
text_input= st.text_area("Enter text to translate: ")
uploaded_file= st.file_uploader("Or upload a file (PDF, TXT , CSV , XLSX):",type=['pdf','txt','csv', 'xlsx'])
language= {
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Hindi": "hi",
    "Chinese": "zh-CN",
    "Arabic": "ar",
    "Italian": "it",
    "Japanese": "ja"
}

selected_language= st.selectbox("Select target language for translation:", list(language.keys()))

if st.button("Translate"):

    #Get text from input or uploaded file
    if uploaded_file is not None:
        text = extract_text_from_file(uploaded_file)
    else:
        text=text_input

    #Validate text input
    if text.strip() =='':
        st.error('Please provide text to translate.')
    else:
        #Translate using gemini
        translate_text= translate_text_gemini(text, language[selected_language])   # FIXED -> use language cod
        st.subheader("Translated Text: ")
        st.write(translate_text)

        #Convert translated text to speech
        audio_file= text_to_speech(translate_text, language[selected_language])
        if os.path.exists(audio_file):  
            st.audio(audio_file, format='audio/mp3')
            with open(audio_file,'rb') as f:
                st.download_button('Download Audio', f, file_name="translated_audio.mp3", mime='audio/mp3')
        else:
            st.error(audio_file)   

