import pandas as pd
import random
from deep_translator import GoogleTranslator


# Load and preprocess the dataset
df = pd.read_csv("heathcare.csv")
df['Symptoms'] = df['Symptoms'].apply(lambda x: [s.strip().lower() for s in str(x).split(',')])

# Basic remedy suggestions for common symptoms
basic_symptom_remedies = {
    "cold": "Take rest, drink warm fluids, and stay hydrated.",
    "fever": "Stay in bed, drink lots of water, and take paracetamol if needed.",
    "cough": "Use cough syrup, stay warm, and avoid cold drinks.",
    "dehydration": "Drink ORS or electrolyte water, avoid outdoor heat, and rest well."
}
messages = [
    "Based on your symptoms, you may have {disease}. {treatment}",
    "It seems like you might be suffering from {disease}. Recommended action: {treatment}",
    "Symptoms indicate {disease}. {treatment}",
    "You may be showing signs of {disease}. Best to follow this advice: {treatment}",
    "Possibly {disease}. Here's what you can do: {treatment}"
]


def get_diagnosis(input_symptoms):
    input_symptoms = [s.strip().lower() for s in input_symptoms]

    # Check if any basic symptoms are present
    basic_matches = [s for s in input_symptoms if s in basic_symptom_remedies]
    if basic_matches:
        suggestions = [basic_symptom_remedies[s] for s in basic_matches]
        return {
            'disease': "Basic Condition",
            'symptoms': basic_matches,
            'treatment': " | ".join(suggestions)
        }

    # Proceed with normal diagnosis logic
    matches = []
    for _, row in df.iterrows():
        disease_symptoms = row['Symptoms']
        match_count = len(set(input_symptoms) & set(disease_symptoms))
        total_symptoms = len(disease_symptoms)

        if match_count > 0:
            match_score = match_count / total_symptoms
            matches.append((match_score, row))

    matches.sort(reverse=True, key=lambda x: x[0])

    if matches:
        top_match = matches[0][1]
        message = random.choice([f"You might have {top_match['Name']}. It's advised to rest and take care.",f"The symptoms suggest a condition like {top_match['Name']}. Please consult a doctor.",f"{top_match['Name']} seems to match your symptoms. Drink fluids and rest.",])
        message_hi = GoogleTranslator(source='en', target='hi').translate(message)
        message_odia=GoogleTranslator(source='en', target='or').translate(message)


        return {
            'message':message,
            'disease': top_match['Name'],
            'symptoms': top_match['Symptoms'],
            'treatment': top_match['Treatments'],
            'inhindi': message_hi,
            'in_odia':message_odia,
        }
    else:
        return {
            'disease': "Unknown",
            'symptoms': [],
            'treatment': "Please consult a doctor for further help.",
        }
