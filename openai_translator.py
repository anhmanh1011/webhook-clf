import openai
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class OpenAITranslator:
    """Class để translate text sử dụng OpenAI API"""
    
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
            self.enabled = True
            logger.info("✅ OpenAI translator enabled")
        else:
            self.enabled = False
            logger.warning("⚠️ OpenAI API key not found. Translation disabled.")
    
    def translate_to_english(self, text: str, source_language: str = "auto") -> Optional[str]:
        """
        Translate text sang tiếng Anh
        
        Args:
            text: Text cần translate
            source_language: Ngôn ngữ nguồn (mặc định auto-detect)
            
        Returns:
            Translated text hoặc None nếu có lỗi
        """
        if not self.enabled:
            logger.warning("OpenAI translator is disabled")
            return None
        
        if not text or text.strip() == "":
            return text
        
        try:
            # Tạo prompt cho translation
            prompt = f"""
            Translate the following text to English. 
            If the text is already in English, return it as is.
            If the text is in Vietnamese or any other language, translate it to English.
            
            Text: "{text}"
            
            Translation:"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful translation assistant. Translate the given text to English. Keep the translation concise and natural."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            translated_text = response.choices[0].message.content.strip()
            logger.info(f"Translation: '{text}' -> '{translated_text}'")
            return translated_text
            
        except Exception as e:
            logger.error(f"Error translating text: {str(e)}")
            return None
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect ngôn ngữ của text
        
        Args:
            text: Text cần detect
            
        Returns:
            Language code hoặc None nếu có lỗi
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""
            Detect the language of this text and return only the language code (e.g., 'en', 'vi', 'fr', etc.):
            
            Text: "{text}"
            
            Language code:"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a language detection assistant. Return only the language code."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            language_code = response.choices[0].message.content.strip().lower()
            logger.info(f"Language detected: '{text}' -> '{language_code}'")
            return language_code
            
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return None
    
    def translate_subject(self, subject: str) -> dict:
        """
        Translate subject và trả về thông tin chi tiết
        
        Args:
            subject: Subject cần translate
            
        Returns:
            Dict với thông tin translation
        """
        if not subject or subject.strip() == "":
            return {
                "original": subject,
                "translated": subject,
                "language_detected": "unknown",
                "translation_status": "no_text"
            }
        
        # Detect language
        detected_lang = self.detect_language(subject)
        
        # Translate to English
        translated_subject = self.translate_to_english(subject, detected_lang)
        
        return {
            "original": subject,
            "translated": translated_subject if translated_subject else subject,
            "language_detected": detected_lang or "unknown",
            "translation_status": "success" if translated_subject else "failed"
        } 