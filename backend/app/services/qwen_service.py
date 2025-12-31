"""
Qwen3-4B AI Service (LM Studio)
ESG rapor içeriği üretimi için
"""
import requests
import json
from typing import Optional, Dict, Any
import time
import re

class QwenESGContentGenerator:
    """Qwen3-4B model ile ESG rapor içeriği üretir (LM Studio)"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:1234", model: str = "qwen/qwen3-4b-2507"):
        """
        Qwen client başlat
        
        Args:
            base_url: LM Studio API endpoint
            model: Model identifier
        """
        self.base_url = base_url
        self.model = model
        self.api_url = f"{base_url}/v1/chat/completions"
        
        # ESG context prompt
        self.system_prompt = """Sen bir ESG (Environmental, Social, Governance) ve karbon emisyonları uzmanısın. 
Türkçe yazıyorsun ve profesyonel, detaylı, analitik raporlar hazırlıyorsun.

Yazı stilinde:
- Markdown formatı kullanma (**, __, # gibi işaretler kullanma)
- Sadece düz metin yaz
- Profesyonel, akademik dil kullan
- Detaylı analizler yap
- Veri yorumlaması yap
- Öneriler sun
- Sayısal verileri açıkla

Türkçe karakterleri doğru kullan (ğ, ü, ş, ı, ö, ç)."""

    def _clean_markdown(self, text: str) -> str:
        """
        Markdown işaretlerini temizle
        
        Args:
            text: Ham metin
            
        Returns:
            Temizlenmiş metin
        """
        if not text:
            return ""
        
        # Markdown bold/italic temizle
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold** -> bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # *italic* -> italic
        text = re.sub(r'__([^_]+)__', r'\1', text)  # __bold__ -> bold
        text = re.sub(r'_([^_]+)_', r'\1', text)  # _italic_ -> italic
        
        # Markdown başlıklar temizle
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)  # # Başlık -> Başlık
        
        # Markdown linkler temizle
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # [text](url) -> text
        
        # Markdown listeler temizle (sadece - ve * işaretlerini kaldır)
        text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
        
        # Markdown kod blokları temizle
        text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Fazla boşlukları temizle
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        return text.strip()

    def generate_content(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        min_words: int = 200
    ) -> str:
        """
        ESG içeriği üret
        
        Args:
            prompt: İçerik prompt'u
            context: Ek bağlam (emission data, ML results vb.)
            max_tokens: Maksimum token sayısı
            temperature: Yaratıcılık (0.7 = dengeli)
            min_words: Minimum kelime sayısı (kalite kontrolü)
            
        Returns:
            Üretilmiş içerik (temizlenmiş)
        """
        try:
            # Context varsa ekle
            context_text = ""
            if context:
                context_text = "\n\nKullanılacak veriler:\n"
                if isinstance(context, dict):
                    if 'results' in context:
                        context_text += "Emisyon Sonuçları:\n"
                        for result in context.get('results', [])[:10]:  # İlk 10
                            context_text += f"- {result.get('activity_name', 'Unknown')}: {result.get('co2e_ton', 0):.2f} ton CO2e ({result.get('scope', 'Unknown')})\n"
                    
                    if 'scope_summary' in context:
                        scope = context['scope_summary']
                        context_text += "\nScope Özeti:\n"
                        for s, v in scope.items():
                            if v > 0:
                                context_text += f"- {s}: {v:.2f} ton CO2e\n"
                    
                    if 'ml_results' in context:
                        ml = context['ml_results']
                        if ml.get('benchmark'):
                            context_text += "\nSektör Benchmark:\n"
                            context_text += f"- Sektör: {ml['benchmark'].get('sector', 'N/A')}\n"
                            if ml['benchmark'].get('metrics'):
                                m = ml['benchmark']['metrics']
                                context_text += f"- Performans: {m.get('rating', 'N/A')}\n"
                        if ml.get('target'):
                            context_text += "\nNet Zero Hedefi:\n"
                            if ml['target'].get('summary'):
                                s = ml['target']['summary']
                                context_text += f"- Hedef Yıl: {s.get('target_year', 'N/A')}\n"
                                context_text += f"- Azaltım: {s.get('total_reduction', 'N/A')}\n"
            
            # Full prompt oluştur
            full_prompt = f"{self.system_prompt}\n\n{context_text}\n\nGörev: {prompt}\n\nLütfen detaylı, profesyonel bir analiz yaz. Markdown formatı kullanma, sadece düz metin yaz."
            
            # API request
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,
                "max_context_length": 10000  # Context uzunluğu 10,000 token
            }
            
            # API çağrısı
            response = requests.post(
                self.api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120  # 2 dakika timeout
            )
            
            if response.status_code != 200:
                error_msg = f"Qwen API hatası: {response.status_code} - {response.text}"
                print(error_msg)
                return f"[HATA: İçerik üretilemedi. {error_msg}]"
            
            try:
                result = response.json()
            except Exception as e:
                return f"[HATA: API yanıtı JSON parse edilemedi: {str(e)}]"
            
            # İçeriği çıkar - Güvenli kontrol
            if not result or not isinstance(result, dict):
                return f"[HATA: API yanıtı geçersiz: {type(result)}]"
            
            choices = result.get('choices', [])
            if not choices or len(choices) == 0:
                return f"[HATA: API yanıtında choices bulunamadı. Yanıt: {result}]"
            
            choice = choices[0]
            if not choice or not isinstance(choice, dict):
                return "[HATA: Choice geçersiz]"
            
            message = choice.get('message')
            if not message or not isinstance(message, dict):
                return "[HATA: Message bulunamadı veya geçersiz]"
            
            content = message.get('content')
            if not content or not isinstance(content, str):
                return "[HATA: Content bulunamadı veya geçersiz]"
            
            # Markdown temizle
            content = self._clean_markdown(content)
            
            # UTF-8 encoding kontrolü
            try:
                content = content.encode('utf-8').decode('utf-8')
            except UnicodeDecodeError:
                content = content.encode('utf-8', errors='ignore').decode('utf-8')
            
            # Minimum kelime kontrolü
            word_count = len(content.split())
            if word_count < min_words:
                print(f"[UYARI] İçerik çok kısa ({word_count} kelime), minimum {min_words} bekleniyordu")
            
            return content
                
        except requests.exceptions.Timeout:
            return "[HATA: API çağrısı zaman aşımına uğradı. LM Studio çalışıyor mu kontrol edin.]"
        except requests.exceptions.ConnectionError:
            return "[HATA: LM Studio'ya bağlanılamadı. LM Studio çalışıyor mu ve http://127.0.0.1:1234 adresinde mi kontrol edin.]"
        except Exception as e:
            error_msg = f"Qwen API hatası: {str(e)}"
            print(error_msg)
            return f"[HATA: {error_msg}]"

    def test_connection(self) -> bool:
        """LM Studio bağlantısını test et"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            return response.status_code == 200
        except:
            return False

