import google.generativeai as genai
from app.core.config import settings
import json
from typing import Dict, Any

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-lite-preview-02-05')
        else:
            self.model = None

    async def analyze_journal(self, content: str, account_context: dict = None) -> Dict[str, Any]:
        """
        Analyzes journal entry/chat message and provides supportive AI coaching.
        """
        if not self.model:
            return {
                "sentiment_score": 0.0,
                "emotional_tags": ["no_ai_key"],
                "ai_feedback": "I am offline (API Key Missing)."
            }

        ctx = ""
        if account_context:
            ctx = f"Stats: Bal ${account_context.get('balance',0):.0f}, DL ${account_context.get('current_daily_loss',0):.0f}"

        prompt = f"""
        Act as a Trading Coach. {ctx}
        User: "{content}"
        Reply JSON: {{ "sentiment_score": float, "emotional_tags": [str], "feedback": "short supportive tip" }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Simple cleanup for json parsing if needed
            text = response.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(text)
            return {
                "sentiment_score": data.get("sentiment_score", 0.0),
                "emotional_tags": data.get("emotional_tags", []),
                "ai_feedback": data.get("feedback", "No feedback generated.")
            }
        except Exception as e:
            print(f"Gemini Error (Falling back to local): {e}")
            # Fallback Heuristics
            content_lower = content.lower()
            tags = []
            feedback = "I'm having trouble connecting to the neural network (Quota), but I'm still here. "
            
            if any(w in content_lower for w in ['fear', 'scared', 'afraid', 'loss', 'lost', 'break']):
                tags = ['fear', 'anxiety']
                score = -0.5
                feedback += "It sounds like you're under pressure. Remember: stick to your plan. Stop trading if you are emotional."
            elif any(w in content_lower for w in ['greed', 'win', 'won', 'profit', 'easy']):
                tags = ['greed', 'overconfidence']
                score = 0.5
                feedback += "Great result, but stay humble. Don't give it back. Lock in your profits."
            else:
                tags = ['neutral']
                score = 0.0
                feedback += "Keep journaling. Tracking your state is the first step to mastery. What's your next move?"

            return {
                "sentiment_score": score,
                "emotional_tags": tags,
                "ai_feedback": feedback
            }

gemini_service = GeminiService()
