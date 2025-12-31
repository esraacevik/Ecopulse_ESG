"""
Ollama Client
Local LLM (DeepSeek-R1-8B) için client
"""

import requests
from typing import Optional
import time


class OllamaClient:
    """Ollama API client (DeepSeek-R1-8B için)"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "deepseek-r1:8b"):
        """
        Ollama client başlat
        
        Args:
            base_url: Ollama API base URL
            model: Model adı (deepseek-r1:8b, llama3.1:8b, vb.)
        """
        self.base_url = base_url
        self.model = model
        self.timeout = 120  # 2 dakika timeout
    
    def is_available(self) -> bool:
        """Ollama servisinin kullanılabilir olup olmadığını kontrol et"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, max_tokens: int = 4096) -> str:
        """
        Prompt ile içerik üret
        
        Args:
            prompt: Kullanıcı prompt'u
            system_prompt: Sistem prompt'u (opsiyonel)
            max_tokens: Maksimum token sayısı
        
        Returns:
            Üretilen içerik
        """
        try:
            # Full prompt oluştur
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Ollama API'ye istek gönder
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40,
                        "num_predict": max_tokens,
                    }
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                raise Exception(f"Ollama API hatası: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            raise Exception("Ollama API timeout - model çok yavaş yanıt veriyor")
        except requests.exceptions.ConnectionError:
            raise Exception("Ollama servisine bağlanılamadı - Ollama çalışıyor mu?")
        except Exception as e:
            raise Exception(f"Ollama hatası: {str(e)}")

