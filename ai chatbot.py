import nltk
from nltk.tokenize import word_tokenize
import string

# ✅ Download tokenizer (runs once)
nltk.download('punkt')

print("🎓 Welcome to XYZ College Enquiry Chatbot!")
print("Type 'exit' to quit.\n")

# 🎓 College Database
college_info = {
    "courses": [
        "B.Tech (CSE, ECE, Mechanical, Civil)",
        "MBA",
        "B.Sc Computer Science"
    ],
    "fees": {
        "B.Tech": "₹1,00,000/year",
        "MBA": "₹1,50,000/year",
        "B.Sc": "₹70,000/year"
    },
    "admission": "Admission is based on entrance exam followed by counselling.",
    "hostel": "Hostel available for boys and girls. Fee: ₹60,000/year.",
    "contact": "Phone: 9876543210 | Email: info@xyzcollege.com",
    "location": "XYZ College is located in Chennai.",
    "facilities": ["Library", "WiFi", "Labs", "Sports Complex"]
}

# 🎯 Intent Keywords
intents = {
    "courses": ["course", "courses", "branch", "study", "program"],
    "fees": ["fee", "fees", "cost", "price"],
    "admission": ["admission", "apply", "join", "eligibility"],
    "hostel": ["hostel", "accommodation", "stay"],
    "contact": ["contact", "phone", "email"],
    "location": ["location", "where", "place"],
    "facilities": ["facility", "facilities", "lab", "wifi", "sports"],
    "greeting": ["hi", "hello", "hey"]
}

# 🧠 Memory
chat_history = []

# 🔍 Preprocess text
def preprocess(text):
    text = text.lower()

    # Remove punctuation before tokenizing
    text = text.translate(str.maketrans('', '', string.punctuation))

    tokens = word_tokenize(text)
    return tokens

# 🎯 Detect intent
def detect_intent(tokens):
    for intent, keywords in intents.items():
        for word in tokens:
            if word in keywords:
                return intent
    return "unknown"

# 🤖 Generate response
def generate_response(intent):
    if intent == "greeting":
        return "Hello! 👋 How can I help you with college enquiries?"

    elif intent == "courses":
        return "Courses offered:\n- " + "\n- ".join(college_info["courses"])

    elif intent == "fees":
        fees_info = "Fees Structure:\n"
        for course, fee in college_info["fees"].items():
            fees_info += f"- {course}: {fee}\n"
        return fees_info

    elif intent == "admission":
        return college_info["admission"]

    elif intent == "hostel":
        return college_info["hostel"]

    elif intent == "contact":
        return college_info["contact"]

    elif intent == "location":
        return college_info["location"]

    elif intent == "facilities":
        return "Facilities:\n- " + "\n- ".join(college_info["facilities"])

    else:
        return ("Sorry, I didn't understand 🤔\n"
                "You can ask about:\n"
                "- Courses\n- Fees\n- Admission\n- Hostel\n- Contact\n")

# 💬 Chat loop
while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Bot: Thank you! Visit again 😊")
        break

    tokens = preprocess(user_input)
    intent = detect_intent(tokens)
    response = generate_response(intent)

    # Save history
    chat_history.append((user_input, response))

    print("Bot:", response)