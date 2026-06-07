import random

class ChatbotService:
    """Generative supportive dialogue service using Gen-Z supportive tones."""
    
    @staticmethod
    def generate_response(message: str) -> str:
        """Parses message semantic triggers and returns tailored supportive remarks."""
        msg_lower = message.strip().lower()
        
        # 1. Gen-Z Keyword Matching Dictionaries
        stress_responses = [
            "Hey 😭 you've been carrying a lot lately. Real talk, you're doing amazing. Maybe your brain needs a small reset? 💙",
            "Exam panic is so real, bestie. But remember, your grades do NOT define your vibe or your worth. Let's take a deep breath together. 📚",
            "Exhausted? Honestly, same. Please promise me you'll shut down the academic tabs for 15 mins. Your mental health is way more important! 🛌"
        ]
        
        anxiety_responses = [
            "I'm here with you 💙 Take a slow breath. Inhale for 4, hold for 4, exhale for 4. You are safe, and we can get through this loop. 😌",
            "Overthinking is literally so exhausting 😭 Remember that thoughts are just thoughts, they aren't facts. Ground yourself, you got this. ✨",
            "Hey, the panic will pass. Focus on 3 things you can see right now. Let's get out of that worry spiral. I'm right here. 💙"
        ]
        
        sad_responses = [
            "I'm sending you the biggest digital hug right now 😭 Feeling lonely is so heavy, but please remember you're not alone. I'm here. 🥺",
            "It's completely okay to not be okay today. Cry it out if you need to, no judgment here. I'm always ready to listen. 💙",
            "Life is being a lot right now. Be extra gentle with yourself today. You are worthy of love, care, and quiet breaks. ✨"
        ]
        
        burnout_responses = [
            "Academic pressure is literally a menace. You cannot pour from an empty cup. Time to close the laptop and grab some water! 💙",
            "You are doing so much, of course you're burnt out. Let's commit to a screen-free evening. Your peace is worth it. 🛌",
            "Please prioritize your sleep tonight, bestie. The work can wait, but your sanity can't. You've got this. ✨"
        ]
        
        general_responses = [
            "Hey! Glad you checked in. How's your energy level today? Remember to drink some water and be nice to yourself. 💙",
            "I'm always in your corner! Whether it's study panic or just venting, Aira has your back. What's on your mind? ✨",
            "You are doing better than you think. Keep taking it one day, or even one hour, at a time. Sending positive energy your way! 🚀"
        ]
        
        # 2. Trigger Checks
        if any(w in msg_lower for w in ["stressed", "exhaust", "tire", "pressure", "grades", "exam", "fail"]):
            return random.choice(stress_responses)
        if any(w in msg_lower for w in ["anxious", "worry", "panic", "scare", "shake", "nervous"]):
            return random.choice(anxiety_responses)
        if any(w in msg_lower for w in ["sad", "lonely", "melancholy", "cry", "hopeless", "depress"]):
            return random.choice(sad_responses)
        if any(w in msg_lower for w in ["burnout", "saturated", "done", "give up"]):
            return random.choice(burnout_responses)
            
        return random.choice(general_responses)
