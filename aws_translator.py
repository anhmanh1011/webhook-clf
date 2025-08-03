import boto3
import os
import logging
from typing import Optional
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

class AWSTranslator:
    """Class để translate text sử dụng AWS Translate API"""
    
    def __init__(self):
        self.region = os.environ.get('AWS_REGION', 'us-east-1')
        self.access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        self.secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        
        if self.access_key and self.secret_key:
            try:
                self.translate_client = boto3.client(
                    'translate',
                    region_name=self.region,
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key
                )
                self.enabled = True
                logger.info("✅ AWS Translate enabled")
            except Exception as e:
                self.enabled = False
                logger.error(f"❌ Failed to initialize AWS Translate: {str(e)}")
        else:
            self.enabled = False
            logger.warning("⚠️ AWS credentials not found. Translation disabled.")
    
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
            logger.warning("AWS Translate is disabled")
            return None
        
        if not text or text.strip() == "":
            return text
        
        try:
            # Nếu source_language là "auto", AWS sẽ tự động detect
            if source_language == "auto":
                source_language = "auto"
            else:
                # Map language codes nếu cần
                source_language = self._map_language_code(source_language)
            
            response = self.translate_client.translate_text(
                Text=text,
                SourceLanguageCode=source_language,
                TargetLanguageCode='en'
            )
            
            translated_text = response['TranslatedText']
            detected_language = response.get('SourceLanguageCode', source_language)
            
            logger.info(f"Translation: '{text}' -> '{translated_text}' (detected: {detected_language})")
            return translated_text
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UnsupportedLanguagePairException':
                logger.warning(f"Unsupported language pair: {source_language} -> en")
                return text  # Return original text if translation not supported
            else:
                logger.error(f"AWS Translate error: {str(e)}")
                return None
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
        
        if not text or text.strip() == "":
            return None
        
        try:
            response = self.translate_client.translate_text(
                Text=text,
                SourceLanguageCode='auto',
                TargetLanguageCode='en'
            )
            
            detected_language = response.get('SourceLanguageCode', 'unknown')
            logger.info(f"Language detected: '{text}' -> '{detected_language}'")
            return detected_language
            
        except ClientError as e:
            logger.error(f"AWS Translate error in language detection: {str(e)}")
            return None
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
    
    def _map_language_code(self, language_code: str) -> str:
        """
        Map language codes để tương thích với AWS Translate
        
        Args:
            language_code: Language code cần map
            
        Returns:
            Mapped language code
        """
        # AWS Translate sử dụng ISO 639-1 language codes
        language_mapping = {
            'vi': 'vi',      # Vietnamese
            'en': 'en',      # English
            'fr': 'fr',      # French
            'de': 'de',      # German
            'es': 'es',      # Spanish
            'it': 'it',      # Italian
            'pt': 'pt',      # Portuguese
            'ru': 'ru',      # Russian
            'ja': 'ja',      # Japanese
            'ko': 'ko',      # Korean
            'zh': 'zh',      # Chinese (Simplified)
            'ar': 'ar',      # Arabic
            'hi': 'hi',      # Hindi
            'th': 'th',      # Thai
        }
        
        return language_mapping.get(language_code.lower(), language_code)
    
    def get_supported_languages(self) -> list:
        """
        Lấy danh sách ngôn ngữ được hỗ trợ
        
        Returns:
            List các language codes được hỗ trợ
        """
        if not self.enabled:
            return []
        
        try:
            response = self.translate_client.list_languages()
            languages = [lang['LanguageCode'] for lang in response['Languages']]
            logger.info(f"Supported languages: {languages}")
            return languages
        except Exception as e:
            logger.error(f"Error getting supported languages: {str(e)}")
            return [] 