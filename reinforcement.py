from collections import defaultdict

class PromptOptimizationRL:
    def __init__(self):
        self.parameters = {
            'empathy_level': 0.5,
            'technique_focus': 0.5,
            'specificity': 0.5,
            'professional_tone': 0.5
        }
        
        self.learning_rate = 0.1
        
        self.state_parameters = defaultdict(lambda: self.parameters.copy())
        
        self.last_state = None
        self.last_parameters = None
        
    def identify_state(self, message):
        emotions = {
            'anxious': ['anxious', 'anxiety', 'nervous', 'worry', 'scared', 'fear', 'stress', 'stressed'],
            'sad': ['sad', 'depress', 'unhappy', 'miserable', 'down', 'low', 'blue'],
            'angry': ['angry', 'mad', 'frustrated', 'irritated', 'annoyed', 'upset'],
            'happy': ['happy', 'good', 'great', 'wonderful', 'joy', 'excited', 'positive'],
            'overwhelmed': ['overwhelm', 'too much', 'exhausted', 'burnout', 'burned out'],
            'lonely': ['lonely', 'alone', 'isolated', 'no friends', 'no one']
        }
        
        message_lower = message.lower()
        detected_states = []
        
        for emotion, keywords in emotions.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_states.append(emotion)
        
        if not detected_states:
            detected_states = ['neutral']
            
        return '+'.join(sorted(detected_states))
    
    def generate_optimized_prompt(self, message):
        state = self.identify_state(message)
        
        params = self.state_parameters[state].copy()
        
        self.last_state = state
        self.last_parameters = params.copy()
        
        modifiers = []
        
        if params['empathy_level'] > 0.7:
            modifiers.append("Be very empathetic and warm in your response. Acknowledge and validate the user's feelings.")
        elif params['empathy_level'] < 0.3:
            modifiers.append("Focus more on solutions than emotional validation.")
            
        if params['technique_focus'] > 0.7:
            modifiers.append("Suggest specific exercises or techniques the user can try immediately.")
        elif params['technique_focus'] < 0.3:
            modifiers.append("Focus more on understanding than providing specific techniques.")
            
        if params['specificity'] > 0.7:
            modifiers.append("Provide detailed, specific advice rather than general statements.")
        elif params['specificity'] < 0.3:
            modifiers.append("Provide brief, concise guidance.")
            
        if params['professional_tone'] > 0.7:
            modifiers.append("Use professional therapeutic language and concepts.")
        elif params['professional_tone'] < 0.3:
            modifiers.append("Use a warm, conversational tone like talking to a friend.")
            
        prompt_guidance = " ".join(modifiers)
        
        prompt = f"""Answer as a mental health therapist in English language only. Reply within 100 words.
        {prompt_guidance}
        Answer only mental health related questions, if not reply 'I cannot answer that question'.
        User message: {message}"""
        
        return prompt
        
    def process_feedback(self, feedback_type):
        if not self.last_state or not self.last_parameters:
            return
            
        state = self.last_state
        current_params = self.state_parameters[state]
        
        if feedback_type == "helpful":
            for param, value in self.last_parameters.items():
                current_params[param] = current_params[param] * (1 - self.learning_rate) + value * self.learning_rate
                
        elif feedback_type == "more_empathy":
            current_params['empathy_level'] = min(1.0, current_params['empathy_level'] + self.learning_rate)
            current_params['professional_tone'] = max(0.0, current_params['professional_tone'] - self.learning_rate)
            
        elif feedback_type == "more_practical":
            current_params['technique_focus'] = min(1.0, current_params['technique_focus'] + self.learning_rate)
            current_params['specificity'] = min(1.0, current_params['specificity'] + self.learning_rate)
            
        elif feedback_type == "too_vague":
            current_params['specificity'] = min(1.0, current_params['specificity'] + self.learning_rate)
            
        elif feedback_type == "not_helpful":
            for param in current_params:
                adjustment = (0.5 - self.last_parameters[param]) * self.learning_rate
                current_params[param] = max(0.0, min(1.0, current_params[param] + adjustment))