import json
import subprocess
import sys
import os
from pathlib import Path
import google.generativeai as genai
from typing import Dict, Any, Optional, Tuple
import time

# Selenium imports for automation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TimParkPaymentTool:
    """
    Tool pentru automatizarea plății parcării în Timișoara.
    Analizează intenția utilizatorului și execută scriptul de automatizare dacă este necesar.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inițializează tool-ul cu configurația specificată.
        
        Args:
            config: Configurația tool-ului din agent_config.json
        """
        self.config = config
        self.enabled = config.get("use_timpark_payment", False)
        
        if self.enabled:
            # Configurare Gemini API
            api_key = os.getenv('GEMINI_KEY')
            if not api_key:
                raise ValueError("GEMINI_KEY nu este setată în variabilele de mediu")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name=config["model"],
                generation_config={
                    "temperature": config["temperature"],
                    "max_output_tokens": config["max_tokens"]
                }
            )
            
            # Încărcare system prompt
            self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """Încarcă system prompt-ul pentru analiza intenției utilizatorului."""
        try:
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up to src directory, then to instructions/platire_timpark
            prompt_path = os.path.join(script_dir, "..", "instructions", "platire_timpark", "system_prompt.txt")
            prompt_path = os.path.normpath(prompt_path)
            
            if not os.path.exists(prompt_path):
                raise FileNotFoundError(f"System prompt nu a fost găsit la: {prompt_path}")
            
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"❌ Error: system_prompt.txt file not found at {prompt_path}")
            print("Expected location: src/instructions/platire_timpark/system_prompt.txt")
            raise
        except Exception as e:
            print(f"❌ Error loading system prompt: {e}")
            raise
    
    def analyze_user_intent(self, user_query: str) -> Dict[str, Any]:
        """
        Analizează intenția utilizatorului folosind Gemini API.
        
        Args:
            user_query: Interogarea utilizatorului
            
        Returns:
            Dict cu rezultatul analizei: {"activare_tool": bool, "numar_ore": str}
        """
        if not self.enabled:
            return {"activare_tool": False, "numar_ore": "1h"}
        
        try:
            # Construire prompt complet
            full_prompt = f"{self.system_prompt}\n\nInterogare Utilizator: \"{user_query}\""
            
            # Apel către Gemini API
            response = self.model.generate_content(full_prompt)
            response_text = response.text.strip()
            
            # Parse JSON response
            try:
                # Handle markdown code blocks if present
                response_text_clean = response_text.strip()
                
                # Check if response is wrapped in markdown code blocks
                if response_text_clean.startswith('```json') and response_text_clean.endswith('```'):
                    # Extract JSON content from between the code blocks
                    json_start = response_text_clean.find('```json') + 7  # Length of '```json'
                    json_end = response_text_clean.rfind('```')
                    response_text_clean = response_text_clean[json_start:json_end].strip()
                elif response_text_clean.startswith('```') and response_text_clean.endswith('```'):
                    # Handle generic code blocks
                    json_start = response_text_clean.find('```') + 3
                    json_end = response_text_clean.rfind('```')
                    response_text_clean = response_text_clean[json_start:json_end].strip()
                
                result = json.loads(response_text_clean)
                
                # Validare rezultat
                if not isinstance(result, dict):
                    raise ValueError("Răspunsul nu este un obiect JSON valid")
                
                if "activare_tool" not in result or "numar_ore" not in result:
                    raise ValueError("Răspunsul nu conține câmpurile necesare")
                
                # Validare valori
                valid_durations = [
                    "30min", "1h", "1h 30min", "2h", "2h 30min", "3h", "3h 30min", 
                    "4h", "4h 30min", "5h", "5h 30min", "6h", "6h 30min", "7h", 
                    "7h 30min", "8h", "8h 30min", "9h", "9h 30min", "10h", 
                    "10h 30min", "11h", "11h 30min", "12h"
                ]
                
                if result["numar_ore"] not in valid_durations:
                    result["numar_ore"] = "1h"  # Default fallback
                
                return result
                
            except json.JSONDecodeError as e:
                print(f"⚠️ Eroare la parsarea JSON din răspunsul Gemini: {e}")
                print(f"Răspuns raw: {response_text}")
                print(f"Răspuns curățat: {response_text_clean}")
                return {"activare_tool": False, "numar_ore": "1h"}
                
        except Exception as e:
            print(f"❌ Eroare la analiza intenției cu Gemini: {e}")
            return {"activare_tool": False, "numar_ore": "1h"}
    
    def execute_payment_automation(self, numar_ore: str) -> Dict[str, Any]:
        """
        Execută automatizarea plății parcării folosind Selenium.
        Integrează direct logica din timpark_autocomplete.py.
        
        Args:
            numar_ore: Durata parcării (ex: "2h", "1h 30min")
            
        Returns:
            Dict cu rezultatul execuției
        """
        print(f"🚗 Începând automatizarea plății parcării pentru {numar_ore}")
        
        # ================================================
        #            DATELE PRESETATE (din scriptul original)
        # ================================================
        numar_masina = "TM99LAC"
        oras_dorit   = "Timisoara"                    # fără diacritice, exact cum apare în lista <select> Oraș (pag. 1)
        zona_dorita  = "Timisoara Zona Autocare 12h - 15.00 LEI"  # exact textul din lista "Selectați zona/durata" (pag. 1)
        perioada_dorita = numar_ore  # DINAMIC - setat din parametrul primit!

        # Date facturare (pagina 2):
        email_utilizator   = "exemplu@domeniu.ro"
        telefon_utilizator = "07xxxxxxxx"
        nume_familie       = "Popescu"
        prenume_utilizator = "Ion"
        judet_dorit        = "Timis"      # fără diacritice, exact cum apare în <select> Județ
        oras_billing       = "Timisoara"  # text liber (pag. 2)
        adresa_billing     = "Strada Exemplu, Nr. 10"
        
        driver = None
        
        try:
            # 1) Deschidem Chrome și pagina inițială
            print("🌐 Deschid browserul Chrome...")
            driver = webdriver.Chrome()
            driver.maximize_window()
            driver.get("https://pay.tpark.io/page/parcare.html?ios=0")

            wait = WebDriverWait(driver, 20)

            # ===============================================
            #  PARTEA I: completarea primei pagini (Detalii plată)
            # ===============================================
            print("📝 Completez prima pagină (Detalii plată)...")
            
            # --- 1.1 Completăm "Număr înmatriculare" ---
            inputuri = driver.find_elements(By.TAG_NAME, "input")
            inputuri[0].clear()
            inputuri[0].send_keys(numar_masina)
            print(f"✅ Număr de înmatriculare completat: {numar_masina}")

            # --- 1.2 Selectăm "Oraș" (primul <select>) ---
            selects = driver.find_elements(By.TAG_NAME, "select")
            oras_dropdown = selects[0]
            select_oras = Select(oras_dropdown)

            # Așteptăm până apare exact 'Timisoara' în listă
            for _ in range(20):
                opt_texts = [opt.text for opt in select_oras.options]
                if oras_dorit in opt_texts:
                    break
                time.sleep(0.5)
                select_oras = Select(driver.find_elements(By.TAG_NAME, "select")[0])
            else:
                raise Exception(f"❌ Nu am găsit '{oras_dorit}' în lista de orașe (pag. 1).")

            select_oras.select_by_visible_text(oras_dorit)
            print(f"✅ Oraș selectat: {oras_dorit}")

            # --- 1.3 Selectăm "Zonă/Durata" (al doilea <select>) ---
            zona_dropdown = driver.find_elements(By.TAG_NAME, "select")[1]
            select_zona = Select(zona_dropdown)

            for _ in range(20):
                opt_zone = [opt.text for opt in select_zona.options]
                if zona_dorita in opt_zone:
                    break
                time.sleep(0.5)
                select_zona = Select(driver.find_elements(By.TAG_NAME, "select")[1])
            else:
                raise Exception(f"❌ Nu am găsit '{zona_dorita}' în lista de zone (pag. 1).")

            select_zona.select_by_visible_text(zona_dorita)
            print(f"✅ Zonă selectată: {zona_dorita}")

            # --- 1.4 Click pe butonul "Continuă plată" (pagina 1) ---
            btn_continua_p1 = driver.find_element(
                By.XPATH,
                "//button[contains(normalize-space(.), 'Continuă plată') or contains(normalize-space(.), 'Continuă plata')]"
            )
            btn_continua_p1.click()
            print("➡ Am apăsat 'Continuă plată' pe pagina 1.")

            # ===============================================
            #   PARTEA II: completarea paginii a doua (Date facturare)
            # ===============================================
            print("📝 Completez a doua pagină (Date facturare)...")
            
            # 2.1 Așteptăm până apare câmpul "E-mail" (pagina 2)
            email_input = wait.until(EC.presence_of_element_located((
                By.XPATH, "//input[@placeholder='E-mail']"
            )))
            time.sleep(10)

            # --- 2.2 Completăm "E-mail" și "Număr de telefon" ---
            email_input.clear()
            email_input.send_keys(email_utilizator)
            print(f"✅ E-mail completat (pag. 2): {email_utilizator}")

            phone_input = driver.find_element(By.XPATH, "//input[@placeholder='Număr de telefon']")
            phone_input.clear()
            phone_input.send_keys(telefon_utilizator)
            print(f"✅ Număr de telefon completat (pag. 2): {telefon_utilizator}")

            # --- 2.3 Completăm "Nume familie" și "Prenume" ---
            lastname_input = driver.find_element(By.XPATH, "//input[@placeholder='Nume familie']")
            lastname_input.clear()
            lastname_input.send_keys(nume_familie)
            print(f"✅ Nume familie completat (pag. 2): {nume_familie}")

            firstname_input = driver.find_element(By.XPATH, "//input[@placeholder='Prenume']")
            firstname_input.clear()
            firstname_input.send_keys(prenume_utilizator)
            print(f"✅ Prenume completat (pag. 2): {prenume_utilizator}")

            # --- 2.4 Selectăm "Județ" (dropdown) ---
            # Găsim dropdown-ul Județ după placeholder-ul său inițial "Selectați județul"
            judet_dropdown = driver.find_element(By.XPATH, "//select[option[contains(text(),'Selectați județul')]]")
            select_judet = Select(judet_dropdown)

            # Așteptăm până apare exact "Timis"
            for _ in range(20):
                lista_judete = [opt.text for opt in select_judet.options]
                if judet_dorit in lista_judete:
                    break

                select_judet = Select(driver.find_element(By.XPATH, "//select[option[contains(text(),'Selectați județul')]]"))
            else:
                raise Exception(f"❌ Nu am găsit '{judet_dorit}' în lista de județe (pag. 2).")

            select_judet.select_by_visible_text(judet_dorit)
            print(f"✅ Județ selectat (pag. 2): {judet_dorit}")

            # --- 2.5 Completăm "Oraș" (câmp text) ---
            city_input = driver.find_element(By.XPATH, "//input[@placeholder='Oraş']")
            city_input.clear()
            city_input.send_keys(oras_billing)
            print(f"✅ Oraș facturare completat (pag. 2): {oras_billing}")

            # --- 2.6 Completăm "Adresă" ---
            address_input = driver.find_element(By.XPATH, "//input[@placeholder='Adresă']")
            address_input.clear()
            address_input.send_keys(adresa_billing)
            print(f"✅ Adresă completată (pag. 2): {adresa_billing}")

            # --- 2.7 Click pe butonul "Continuă plată" (pagina 2) ---
            btn_continua_p2 = driver.find_element(
                By.XPATH,
                "//button[contains(normalize-space(.), 'Continuă plată') or contains(normalize-space(.), 'Continuă plata')]"
            )
            btn_continua_p2.click()
            print("➡ Am apăsat 'Continuă plată' pe pagina 2.")

            # Pauză finală ca să poată fi procesată plata
            print("⏳ Aștept finalizarea procesului de plată...")
            time.sleep(5)  # Reduced from 3600 seconds for testing
            
            print(f"🎉 Automatizarea plății parcării pentru {numar_ore} a fost completată cu succes!")
            
            return {
                "success": True,
                "output": f"Automatizarea plății parcării pentru {numar_ore} executată cu succes",
                "error": "",
                "numar_ore_procesat": numar_ore
            }

        except Exception as e:
            error_msg = f"Eroare în timpul automatizării: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "output": "",
                "numar_ore_procesat": numar_ore
            }
        
        finally:
            # Cleanup - închide browserul
            if driver:
                try:
                    print("🧹 Închid browserul...")
                    driver.quit()
                except:
                    pass
    
    def process(self, user_query: str) -> Dict[str, Any]:
        """
        Procesează interogarea utilizatorului - analizează intenția și execută automatizarea dacă este necesar.
        
        Args:
            user_query: Interogarea utilizatorului
            
        Returns:
            Dict cu rezultatul procesării complete
        """
        if not self.enabled:
            return {
                "tool_enabled": False,
                "message": "Tool-ul TimPark nu este activat în configurație"
            }
        
        # Pasul 1: Analizează intenția utilizatorului
        print("🔍 Analizez intenția utilizatorului pentru plata parcării...")
        intent_analysis = self.analyze_user_intent(user_query)
        
        result = {
            "tool_enabled": True,
            "user_query": user_query,
            "intent_analysis": intent_analysis,
            "tool_activated": intent_analysis["activare_tool"],
            "duration": intent_analysis["numar_ore"]
        }
        
        # Pasul 2: Execută automatizarea dacă este necesar
        if intent_analysis["activare_tool"]:
            print(f"✅ Tool activat! Execut automatizarea plății pentru {intent_analysis['numar_ore']}")
            
            automation_result = self.execute_payment_automation(intent_analysis["numar_ore"])
            result["automation_result"] = automation_result
            
            if automation_result["success"]:
                result["message"] = f"✅ Automatizarea plății parcării a fost executată cu succes pentru {intent_analysis['numar_ore']}"
            else:
                result["message"] = f"❌ Eroare la automatizarea plății: {automation_result['error']}"
        else:
            print("ℹ️ Tool-ul nu va fi activat - intenția de plată nu a fost detectată")
            result["message"] = "ℹ️ Nu am detectat o intenție clară de plată a parcării în Timișoara"
        
        return result

def create_timpark_payment_tool(config: Dict[str, Any]) -> TimParkPaymentTool:
    """Factory function pentru crearea tool-ului."""
    return TimParkPaymentTool(config) 