import streamlit as st
from diagnosis_data import get_diagnosis
from doctor import get_nearest_clinic
from utils.speech_utils import recognize_speech
from streamlit_js_eval import get_geolocation

import pandas as pd

from deep_translator import GoogleTranslator
import random

messages = [
    "Based on your symptoms, you may have {disease}. {treatment}",
    "It seems like you might be suffering from {disease}. Recommended action: {treatment}",
    "Symptoms indicate {disease}. {treatment}",
    "You may be showing signs of {disease}. Best to follow this advice: {treatment}",
    "Possibly {disease}. Here's what you can do: {treatment}"
]

# Load clinic data
clinic_df = pd.read_excel("Odisha_Hospitals (1).xlsx")


st.set_page_config(page_title="Health Diagnosis Bot", layout="centered")

# Language selection
st.sidebar.title("🌐 Choose Language")
language = st.sidebar.selectbox("Select Language", ["English", "Hindi", "Odia"])
st.session_state["lang"] = language

st.markdown("<div class='main'>", unsafe_allow_html=True)
st.image("https://cdn-icons-png.flaticon.com/512/2966/2966486.png", width=100)


 
 
# District-town mapping with translations
districts_translated = {
    "English": {
  "Cuttack": ["Cuttack", "Choudwar", "Narsinghpur", "Athagarh"],
  "Khordha": ["Bhubaneswar", "Jatni", "Begunia", "Balugaon"],
  "Puri": ["Puri", "Konark", "Satyabadi", "Delang"],
  "Balasore": ["Balasore", "Nilagiri", "Jaleswar", "Soro"],
  "Sambalpur": ["Sambalpur", "Burla", "Hirakud", "Rengali"],
  "Ganjam": ["Berhampur", "Chhatrapur", "Bhanjanagar", "Aska"],
  "Angul": ["Angul", "Talcher", "Athmallik", "Nalconagar"],
  "Balangir": ["Balangir", "Titlagarh", "Kantabanji", "Patnagarh"],
  "Boudh (Baudh)": ["Boudhgarh", "Baunsuni", "Kantamal", "Manamunda"],
  "Bargarh": ["Bargarh", "Barapali", "Padmapur", "Sohela"],
  "Bhadrak": ["Bhadrak", "Basudevpur", "Chandabali", "Dhamanagar"],
  "Jharsuguda": ["Jharsuguda", "Brajarajnagar", "Belpahar", "Bandhbahal"],
  "Dhenkanal": ["Dhenkanal", "Bhuban", "Kamakshyanagar", "Saranga"],
  "Jajpur": ["Jajpur", "Byasanagar", "Sayadpur", "Kabatabandha"],
  "Jagatsinghapur": ["Jagatsinghapur", "Paradip", "Paradipgarh", "Krushnanandapur"],
  "Keonjhar (Kendujhar)": ["Kendujhar", "Barbil", "Champua", "Jajanga"],
  "Kalahandi": ["Bhawanipatna", "Junagarh", "Kesinga", "Madhanpur Rampur"],
  "Koraput": ["Koraput", "Jeypore", "Sunabeda", "Kotpad"],
  "Kendrapara": ["Kendrapara", "Pattamundai", "Rajkanika", "Aul"],
  "Malkangiri": ["Malkangiri", "Balimela", "Chitrakonda", "Sunki"],
  "Mayurbhanj": ["Baripada", "Rairangpur", "Udala", "Karanjia"],
  "Nabarangapur": ["Nabarangpur", "Umerkote", "Papadahandi", "Raighar"],
  "Nuapada": ["Nuapada", "Khariar", "Khariar Road", "Komna"],
  "Nayagarh": ["Nayagarh", "Itamati", "Chandapur", "Odagaon"],
  "Rayagada": ["Rayagada", "Gunupur", "Kashipur", "Tikiri"],
  "Subarnapur (Sonepur)": ["Sonapur", "Binika", "Tarbha", "Sonepur Town"],
  "Sundargarh": ["Sundargarh", "Rourkela", "Rajgangpur", "Biramitrapur"]
},

  "Hindi": {
  "कटक": ["कटक", "चौद्वार", "नरसिंहपुर", "अठगड़"],
  "खोरधा": ["भुवनेश्वर", "जटनी", "बेगुनिया", "बलूगांव"],
  "पुरी": ["पुरी", "कोणार्क", "सत्यवादी", "डेलांग"],
  "बालासोर": ["बालासोर", "निलगिरी", "जलेश्वर", "सोरो"],
  "संभलपुर": ["संभलपुर", "बुरला", "हिराकुड़", "रेंगाली"],
  "गंजाम": ["ब्रह्मपुर", "छत्रपुर", "भंजनगर", "आस्का"],
  "अंगुल": ["अंगुल", "तालचेर", "अथमल्लिक", "नाल्कोनगर"],
  "बलांगीर": ["बलांगीर", "टिटलागढ़", "कांताबांजी", "पटनागढ़"],
  "बौध": ["बौधगढ़", "बौंसुनी", "कांतामाल", "मनमुण्डा"],
  "बरगढ़": ["बरगढ़", "बरपाली", "पदमपुर", "सोहेला"],
  "भद्रक": ["भद्रक", "बसुदेवपुर", "चांदबली", "धामनगर"],
  "झारसुगुड़ा": ["झारसुगुड़ा", "ब्रेजराजनगर", "बेलपाहर", "बन्धबाहाल"],
  "ढेंकानाल": ["ढेंकानाल", "भुवन", "कामाक्ष्यानगर", "सरंगा"],
  "जाजपुर": ["जाजपुर", "ब्यासनगर", "सायदपुर", "कबटबांधा"],
  "जगतसिंहपुर": ["जगतसिंहपुर", "परादीप", "परादीपगढ़", "कृष्णानंदपुर"],
  "केंदुझर": ["केंदुझर", "बरबिल", "चंपुआ", "जाजंगा"],
  "कालाहांडी": ["भवानीपटना", "जुनागढ़", "केसिंगा", "मदनपुर रामपुर"],
  "कोरापुट": ["कोरापुट", "जयपुर", "सुनाबेड़ा", "कोटपद"],
  "केंद्रापाड़ा": ["केंद्रापाड़ा", "पत्तामुंडई", "राजकनिका", "औल"],
  "मलकानगिरी": ["मलकानगिरी", "बालिमेला", "चित्रकोंडा", "सुनकी"],
  "मयूरभंज": ["बारिपदा", "रायरंगपुर", "उडाला", "करंजिया"],
  "नबरंगपुर": ["नबरंगपुर", "उमरकोट", "पापड़ाहांडी", "राइगढ़"],
  "नुआपाड़ा": ["नुआपाड़ा", "खारियार", "खारियार रोड", "कोमना"],
  "नयागढ़": ["नयागढ़", "इतमाटी", "चंदापुर", "ओडागांव"],
  "रायगढ़ा": ["रायगढ़ा", "गुनुपुर", "काशीपुर", "टीकिरी"],
  "सुबर्णपुर": ["सोनपुर", "बिनिका", "तारभा", "सोनपुर टाउन"],
  "सुंदरगढ़": ["सुंदरगढ़", "राउरकेला", "राजगांगपुर", "बिरमित्रापुर"]
}
,
  "Odia": {
  "କଟକ": ["କଟକ", "ଚୌଦ୍ୱାର", "ନରସିଂହପୁର", "ଅଠଗଡ଼"],
  "ଖୋର୍ଦ୍ଧା": ["ଭୁବନେଶ୍ୱର", "ଜଟଣୀ", "ବେଗୁନିଆ", "ବାଲୁଗାଁ"],
  "ପୁରୀ": ["ପୁରୀ", "କୋଣାର୍କ", "ସତ୍ୟବାଦୀ", "ଡେଲାଙ୍ଗ"],
  "ବାଲେଶ୍ୱର": ["ବାଲେଶ୍ୱର", "ନିଳଗିରି", "ଜଲେଶ୍ୱର", "ସୋରୋ"],
  "ସମ୍ବଲପୁର": ["ସମ୍ବଲପୁର", "ବୁର୍ଲା", "ହିରାକୁଦ", "ରେଙ୍ଗାଲି"],
  "ଗଞ୍ଜାମ": ["ବ୍ରହ୍ମପୁର", "ଛତ୍ରପୁର", "ଭଞ୍ଜନଗର", "ଆସ୍କା"],
  "ଅନୁଗୁଳ": ["ଅନୁଗୁଳ", "ତଳଚେର", "ଅଥମଲ୍ଲିକ", "ନାଲ୍କୋନଗର"],
  "ବଲାଙ୍ଗିର": ["ବଲାଙ୍ଗିର", "ଟିଟିଲାଗଡ଼", "କାନ୍ତାବାଞ୍ଜି", "ପଟ୍ନାଗଡ଼"],
  "ବୌଢ଼": ["ବୌଢ଼ଗଡ଼", "ବାଉଁସୁନୀ", "କାନ୍ତାମାଳ", "ମଣମୁଣ୍ଡା"],
  "ବରଗଡ଼": ["ବରଗଡ଼", "ବରପାଲି", "ପଦ୍ମପୁର", "ସୋହେଲା"],
  "ଭଦ୍ରକ": ["ଭଦ୍ରକ", "ବସୁଦେବପୁର", "ଚନ୍ଦାବଳି", "ଧାମନଗର"],
  "ଝାରସୁଗୁଡ଼ା": ["ଝାରସୁଗୁଡ଼ା", "ବ୍ରଜରାଜନଗର", "ବେଳପାହାଡ଼", "ବନ୍ଧବାହାଲ"],
  "ଢେଙ୍କାନାଳ": ["ଢେଙ୍କାନାଳ", "ଭୁବନ", "କାମାକ୍ଷ୍ୟାନଗର", "ସରଙ୍ଗା"],
  "ଜାଜପୁର": ["ଜାଜପୁର", "ବ୍ୟାସନଗର", "ସାୟଦପୁର", "କବଟବନ୍ଧା"],
  "ଜଗତସିଂହପୁର": ["ଜଗତସିଂହପୁର", "ପାରାଦୀପ", "ପାରାଦୀପଗଡ଼", "କୃଷ୍ଣାନନ୍ଦପୁର"],
  "କେନ୍ଦୁଝର": ["କେନ୍ଦୁଝର", "ବରବିଲ", "ଚମ୍ପୁଆ", "ଜାଜଙ୍ଗା"],
  "କଳାହାଣ୍ଡି": ["ଭବାନୀପାଟଣା", "ଜୁନାଗଡ଼", "କେସିଙ୍ଗା", "ମଦନପୁର ରାମପୁର"],
  "କୋରାପୁଟ": ["କୋରାପୁଟ", "ଜୟପୁର", "ସୁନାବେଡ଼ା", "କୋଟପଦ"],
  "କେନ୍ଦ୍ରାପଡ଼ା": ["କେନ୍ଦ୍ରାପଡ଼ା", "ପଟ୍ଟାମୁଣ୍ଡାଇ", "ରାଜକନିକା", "ଔଳ"],
  "ମଲ୍କାନଗିରି": ["ମଲ୍କାନଗିରି", "ବାଳିମେଳା", "ଚିତ୍ରକୋଣ୍ଡା", "ସୁନ୍କି"],
  "ମୟୂରଭଞ୍ଜ": ["ବାରିପଦା", "ରାଇରଙ୍ଗପୁର", "ଉଡ଼ାଳା", "କରଞ୍ଜିଆ"],
  "ନବରଙ୍ଗପୁର": ["ନବରଙ୍ଗପୁର", "ଉମେରକୋଟ", "ପାପଡାହାଣ୍ଡି", "ରାଈଘର"],
  "ନୂଆପଡ଼ା": ["ନୂଆପଡ଼ା", "ଖାରିଆର", "ଖାରିଆର ରୋଡ଼", "କୋମ୍ନା"],
  "ନୟାଗଡ଼": ["ନୟାଗଡ଼", "ଇତମାଟି", "ଚନ୍ଦାପୁର", "ଓଡ଼ାଗାଁ"],
  "ରାୟଗଡ଼ା": ["ରାୟଗଡ଼ା", "ଗୁଣୁପୁର", "କାଶିପୁର", "ଟିକିରି"],
  "ସୁବର୍ଣ୍ଣପୁର": ["ସୋନପୁର", "ବିନିକା", "ତାରଭା", "ସୋନପୁର ଟାଉନ"],
  "ସୁନ୍ଦରଗଡ଼": ["ସୁନ୍ଦରଗଡ଼", "ରାଉରକେଲା", "ରାଜଗାଙ୍ଗପୁର", "ବିରମିତ୍ରାପୁର"]
}

}

# Get current language translation dictionary
t = {
    "English": {
        "app_title": "🤖 AI Health Diagnosis Chatbot",
        "speak_symptoms": "🎙️ Speak Symptoms",
        "input_label": "Enter symptoms (comma-separated):",
        "diagnose_btn": "Diagnose",
        "diagnosis_result": "🩺 Diagnosis Result:",
        "disease": "**Disease:**",
        "symptoms": "**Matching Symptoms:**",
        "treatment": "**Suggested Treatment:**",
        "clinic": "🏥 Nearby Clinic Recommendation:",
        "name": "**Name:**",
        "address": "**Address:**",
        "distance": "**Distance:**",
        "phone": "**Phone:**",
        "warning": "⚠️ Please enter symptoms or speak using the mic button.",
        "location_title": "🗺️ Get Your Location",
        "loc_success": "Location Retrieved Successfully!",
        "lat": "📍 Latitude",
        "lon": "📍 Longitude",
        "accuracy": "⏱️ Accuracy",
        "location_info": "Please allow location access in your browser.",
        "district_label": "📍 Select your District",
        "town_label": "Towns in"
    },
    "Hindi": {
        "app_title": "🤖 एआई स्वास्थ्य निदान चैटबोट",
        "speak_symptoms": "🎙️ लक्षण बोलें",
        "input_label": "लक्षण दर्ज करें (कॉमा से अलग करें):",
        "diagnose_btn": "निदान करें",
        "diagnosis_result": "🩺 निदान परिणाम:",
        "disease": "**बीमारी:**",
        "symptoms": "**मिलते-जुलते लक्षण:**",
        "treatment": "**सुझावित इलाज:**",
        "clinic": "🏥 नजदीकी क्लिनिक सिफारिश:",
        "name": "**नाम:**",
        "address": "**पता:**",
        "distance": "**दूरी:**",
        "phone": "**फोन:**",
        "warning": "⚠️ कृपया लक्षण दर्ज करें या माइक का उपयोग करें।",
        "location_title": "🗺️ अपना स्थान प्राप्त करें",
        "loc_success": "स्थान सफलतापूर्वक प्राप्त हुआ!",
        "lat": "📍 अक्षांश",
        "lon": "📍 देशांतर",
        "accuracy": "⏱️ सटीकता",
        "location_info": "कृपया अपने ब्राउज़र में स्थान की अनुमति दें।",
        "district_label": "📍 अपना ज़िला चुनें",
        "town_label": "शहर (टाउन)"
    },
    "Odia": {
        "app_title": "🤖 ଏଆଇ ସ୍ୱାସ୍ଥ୍ୟ ନିଦାନ ଚାଟବଟ୍",
        "speak_symptoms": "🎙️ ଲକ୍ଷଣ କହନ୍ତୁ",
        "input_label": "ଲକ୍ଷଣ ଲେଖନ୍ତୁ (କମା ଦ୍ୱାରା):",
        "diagnose_btn": "ନିଦାନ କରନ୍ତୁ",
        "diagnosis_result": "🩺 ନିଦାନ ଫଳାଫଳ:",
        "disease": "**ରୋଗ:**",
        "symptoms": "**ମେଳ ମିଳୁଥିବା ଲକ୍ଷଣ:**",
        "treatment": "**ପ୍ରସ୍ତାବିତ ଚିକିତ୍ସା:**",
        "clinic": "🏥 ନିକଟସ୍ଥ କ୍ଲିନିକ ସୁପାରିଶ:",
        "name": "**ନାମ:**",
        "address": "**ଠିକଣା:**",
        "distance": "**ଦୂରତା:**",
        "phone": "**ଫୋନ୍:**",
        "warning": "⚠️ ଦୟାକରି ଲକ୍ଷଣ ଦିଅନ୍ତୁ କିମ୍ବା ମାଇକ୍ ବ୍ୟବହାର କରନ୍ତୁ।",
        "location_title": "🗺️ ଅବସ୍ଥାନ ନିର୍ଣୟ କରନ୍ତୁ",
        "loc_success": "ଅବସ୍ଥାନ ମିଳିଗଲା!",
        "lat": "📍 ଅକ୍ଷାଂଶ",
        "lon": "📍 ଦେଶାଂତର",
        "accuracy": "⏱️ ସଠିକତା",
        "location_info": "ବ୍ରାଉଜରରେ ଅନୁମତି ଦିଅନ୍ତୁ।",
        "district_label": "📍 ଜିଲ୍ଲା ବାଛନ୍ତୁ",
        "town_label": "ସହର (ଟାଉନ୍)"
    }
}[language]

# Title
st.title(t["app_title"])

# District & Town Selection
st.subheader(t["district_label"])
districts = list(districts_translated[language].keys())
selected_district = st.selectbox("District:", districts)

if selected_district:
    towns = districts_translated[language][selected_district]
    selected_town = st.selectbox(f"{t['town_label']} {selected_district}:", towns)
    st.success(f"📌 {selected_district} → {selected_town}")
    st.session_state["district"] = selected_district
    st.session_state["town"] = selected_town

# Voice Input
if st.button(t["speak_symptoms"]):
    spoken_text = recognize_speech()
    if spoken_text:
        st.session_state["symptoms_input"] = spoken_text

# Text Input
#user_input = st.text_input(t["input_label"], 
                          # value=st.session_state.get("symptoms_input", ""))

user_input_1 = st.text_area("लक्षण दर्ज करें (Type your symptoms)", "")
user_input= GoogleTranslator(source='auto', target='en').translate(user_input_1)

st.write("📘 Translated to English:", user_input)

# Diagnosis Section
if st.button(t["diagnose_btn"]):
    if user_input:
        symptoms = user_input.split(',')
        result = get_diagnosis(symptoms)
        st.markdown("### 🧬 Diagnosis Summary")
        
        result["message"] = random.choice(messages).format(disease=result["disease"],treatment=result["treatment"])
        result["inhindi"] = GoogleTranslator(source='en', target='hi').translate(result["message"])
        result["in_odia"] = GoogleTranslator(source='en', target='or').translate(result["message"])


        st.write(result['message'])
        st.write(result['inhindi'])
        st.write(result['in_odia'])


        st.subheader(t["diagnosis_result"])
        st.write(t["disease"], result['disease'])
        st.write(t["symptoms"], ', '.join(result['symptoms']))
        st.write(t["treatment"], result['treatment'])
        # Show clinic(s) from CSV for selected district
        st.subheader(t["clinic"])
        matched_clinics = clinic_df[clinic_df["District"].str.lower() == selected_district.lower()]

        if not matched_clinics.empty:
            for _, clinic in matched_clinics.iterrows():
                st.write(t["name"], clinic["Clinic Name"])
                st.write(t["address"], clinic["Address"])
                st.markdown(f"[🌐 Location Link]({clinic['Location URL']})")
                st.markdown("---")
        else:
            st.warning("🚫 No clinics found for this district.")



