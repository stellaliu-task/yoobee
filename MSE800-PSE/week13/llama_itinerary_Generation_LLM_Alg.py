from together import Together

def instructor_chatbot():
    client = Together(api_key="6a657bd5cbae809515903ff54f27cb7237ad33d21007bc948085b87dd9cff1fe")

    """Command-line AI Itinerary Chatbot."""
    print("Welcome to AI Itinerary recommender! Answer a few questions to get personalized itenary advice.\n")
    
    days = input("How many (days): ")
    location = input("Where is the destination (city name): ")
    age = input("Enter your age: ")
    people = input("Enter how many people:")
    # fitness_goal = input("What is your fitness goal? (e.g., lose weight, build muscle, endurance, etc.): ")
    
    # Construct prompt
    prompt = f"""
    You are a professional trouist recommender. Provide an itinerary recommendation based on user data.
    
    User Details:
    - days: {days} days
    - destination: {location} city
    - Age: {age} years
    - people:{people} number
    
    Based on your personal information, 
    Then, give a structured itinerary with a name of the place, address and short description for each day seperatly in order with maximom three activities in a day.
    """
    
    try:
        response = client.chat.completions.create(
        model="meta-llama/Llama-Vision-Free",
        messages=[{"role": "system", "content": "You are a professional itinerary recommender."},
                      {"role": "user", "content": prompt}],
        max_tokens=3000,
        temperature=0.8,
        stream=True
        )

        print("\n My Name is Chris as AI Itinerary expert:")
        for token in response:
            if hasattr(token, 'choices'):
                print(token.choices[0].delta.content, end='', flush=True)
        
    except Exception as e:
        print("Error communicating with Meta Llama API:", e)

if __name__ == "__main__":
    instructor_chatbot()