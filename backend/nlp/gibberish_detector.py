import math
import re

class GibberishDetector:
    # Common English words/stopwords/pronouns/common verbs/mood words
    COMMON_WORDS = {
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", 
        "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", 
        "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", 
        "theirs", "themselves", "what", "which", "who", "whom", "this", "that", 
        "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", 
        "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", 
        "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", 
        "at", "by", "for", "with", "about", "against", "between", "into", "through", 
        "during", "before", "after", "above", "below", "to", "from", "up", "down", 
        "in", "out", "on", "off", "over", "under", "again", "further", "then", "once",
        "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", 
        "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", 
        "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", 
        "don", "should", "now", "feel", "feeling", "happy", "sad", "stressed", "tired", 
        "good", "bad", "today", "yesterday", "school", "exam", "exams", "study", "work",
        "anxious", "anxiety", "depressed", "depression", "love", "hate", "friend", 
        "friends", "family", "sleep", "sleeping", "screen", "time", "day", "night"
    }

    @staticmethod
    def calculate_entropy(text: str) -> float:
        """Calculate Shannon character entropy of the text."""
        if not text:
            return 0.0
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        entropy = 0.0
        total_chars = len(text)
        for count in char_counts.values():
            p = count / total_chars
            entropy -= p * math.log2(p)
        return entropy

    @classmethod
    def is_gibberish(cls, text: str) -> bool:
        """
        Returns True if the text is classified as gibberish based on:
        1. Vowel density
        2. Maximum consonant cluster length
        3. Shannon character entropy
        4. Common English word presence
        """
        text_clean = text.strip().lower()
        if not text_clean:
            return True

        # Extract only alphabetic letters
        letters = re.sub(r'[^a-z]', '', text_clean)
        if not letters:
            return True # No letters at all (e.g. only punctuation/numbers)

        # 1. Vowel Density Check
        vowels = re.sub(r'[^aeiou]', '', letters)
        vowel_count = len(vowels)
        total_letters = len(letters)
        vowel_density = vowel_count / total_letters if total_letters > 0 else 0
        
        # If vowel density is extremely low (< 15%) or extremely high (> 85%), flag as gibberish
        if total_letters >= 5:
            if vowel_density < 0.15 or vowel_density > 0.85:
                return True

        # 2. Consonant Cluster Check
        # Check for more than 5 consecutive non-vowels (consonants)
        consonant_clusters = re.findall(r'[^aeiou\s\d\W_]{6,}', text_clean)
        if consonant_clusters:
            return True

        # 3. Shannon Character Entropy Check
        entropy = cls.calculate_entropy(text_clean)
        if len(text_clean) >= 10 and entropy < 1.8:
            return True

        # 4. Common English Word Presence
        words = re.findall(r'\b[a-z]+\b', text_clean)
        if not words:
            return True
        
        # Check if at least one word is in our common English dictionary
        matches = sum(1 for w in words if w in cls.COMMON_WORDS)
        if len(words) >= 3 and matches == 0:
            return True

        return False
