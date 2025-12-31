"""
Google Gemini AI Service
ESG ve karbon emisyonları hakkında soruları yanıtlar
"""
import os
import google.generativeai as genai
from typing import Optional, Dict, Any
from app.config import settings

class GeminiESGAssistant:
    """Gemini 2.5 Flash kullanarak ESG asistanı"""
    
    def __init__(self):
        """Gemini API'yi başlat"""
        self.api_key = os.getenv("GEMINI_API_KEY", settings.GEMINI_API_KEY if hasattr(settings, 'GEMINI_API_KEY') else "")
        # Gemini 2.5 Flash model - kullanıcı tarafından belirtilen model adı
        # Eğer bu model adı çalışmazsa, alternatif olarak "gemini-2.0-flash-exp" veya "gemini-1.5-flash" deneyin
        self.model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash-exp")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
        # ESG context prompt
        self.system_prompt = """Sen bir ESG (Environmental, Social, Governance) ve karbon emisyonları uzmanısın. 
Kullanıcılara şu konularda yardımcı olabilirsin:

1. **Scope 1, 2, 3 Emisyonları**: Doğrudan ve dolaylı emisyonların açıklaması
2. **Karbon Ayak İzi Hesaplama**: Metodolojiler ve standartlar
3. **ESG Raporlama**: GRI, CDP, TCFD gibi standartlar
4. **Net Zero ve Carbon Neutrality**: Hedefler ve stratejiler
5. **Yeşil Finans**: Sürdürülebilir finansman araçları
6. **Emisyon Faktörleri**: Farklı aktiviteler için emisyon katsayıları

Türkçe ve İngilizce soruları yanıtlayabilirsin. Yanıtların bilimsel, güncel ve pratik olmalı.
Eğer kullanıcı hesaplama sonuçları paylaşırsa, bunları analiz edebilir ve öneriler sunabilirsin."""

    def answer_question(self, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        ESG sorusunu yanıtla
        
        Args:
            question: Kullanıcının sorusu
            context: Hesaplama sonuçları veya ek bağlam (opsiyonel)
        
        Returns:
            AI'nın yanıtı
        """
        try:
            # Context varsa ekle
            context_text = ""
            if context:
                context_text = f"\n\nKullanıcının mevcut hesaplama sonuçları:\n"
                if isinstance(context, dict):
                    if 'results' in context:
                        for result in context.get('results', []):
                            context_text += f"- {result.get('category', 'Unknown')}: {result.get('co2e', 0):.2f} kg CO2e\n"
                    elif 'total_co2e' in context:
                        context_text += f"Toplam Emisyon: {context.get('total_co2e', 0):.2f} kg CO2e\n"
                        context_text += f"Scope: {context.get('scope', 'Unknown')}\n"
            
            # Prompt oluştur
            full_prompt = f"{self.system_prompt}\n\n{context_text}\n\nKullanıcı Sorusu: {question}\n\nYanıt:"
            
            # Gemini'ye sor
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
            )
            
            return response.text.strip()
            
        except Exception as e:
            error_msg = f"Gemini API hatası: {str(e)}"
            print(error_msg)
            
            # Fallback yanıt
            return f"Üzgünüm, şu anda yanıt veremiyorum. Lütfen daha sonra tekrar deneyin. Hata: {str(e)}"

