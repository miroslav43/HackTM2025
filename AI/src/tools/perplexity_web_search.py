import os
import json
import re
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
CURRENT_DATE = "2025-05-30"  # Data de astăzi pentru context

# Date pentru locațiile din România
ROMANIA_LOCATIONS = {
    "bucharest": {"latitude": 44.4268, "longitude": 26.1025, "name": "București"},
    "timisoara": {"latitude": 45.7489, "longitude": 21.2087, "name": "Timișoara"},
    "cluj": {"latitude": 46.7712, "longitude": 23.6236, "name": "Cluj-Napoca"},
    "constanta": {"latitude": 44.1598, "longitude": 28.6348, "name": "Constanța"},
    "brasov": {"latitude": 45.6427, "longitude": 25.5887, "name": "Brașov"},
    "iasi": {"latitude": 47.1585, "longitude": 27.6014, "name": "Iași"}
}

def validate_date_format(date_string):
    """Validează formatul datei pentru API-ul Perplexity (%m/%d/%Y)"""
    date_regex = r'^(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])/[0-9]{4}$'
    return re.match(date_regex, date_string) is not None

def create_filename_from_question(question, timestamp=None):
    """Creează un nume de fișier sigur din întrebare și timestamp"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Curăță întrebarea pentru utilizarea ca nume de fișier
    clean_question = re.sub(r'[^\w\s-]', '', question)  # Elimină caractere speciale
    clean_question = re.sub(r'\s+', '_', clean_question)  # Înlocuiește spațiile cu underscore
    clean_question = clean_question[:50]  # Limitează lungimea
    clean_question = clean_question.strip('_')  # Elimină underscore-urile de la început/sfârșit
    
    if not clean_question:
        clean_question = "intrebare_cautare"
    
    filename = f"{clean_question}_{timestamp}.txt"
    return filename

def get_romania_location_filter(city_hint=None):
    """Obține filtrul de locație pentru România cu coordonate opționale specifice pentru oraș"""
    base_filter = {"country": "RO"}
    
    if city_hint:
        # Verifică dacă cererea menționează un oraș românesc specific
        city_hint_lower = city_hint.lower()
        for city_key, city_data in ROMANIA_LOCATIONS.items():
            if city_key in city_hint_lower or city_data["name"].lower() in city_hint_lower:
                base_filter.update({
                    "latitude": city_data["latitude"],
                    "longitude": city_data["longitude"]
                })
                print(f"🏙️  Oraș detectat: {city_data['name']} - folosesc coordonate specifice")
                return base_filter
    
    # Implicit la coordonatele Bucureștiului pentru căutări în toată România
    base_filter.update({
        "latitude": ROMANIA_LOCATIONS["bucharest"]["latitude"],
        "longitude": ROMANIA_LOCATIONS["bucharest"]["longitude"]
    })
    print("🇷🇴 Folosesc căutare pentru România cu coordonatele Bucureștiului")
    return base_filter

def load_system_prompt():
    """Încarcă prompt-ul de sistem din fișier și îl îmbunătățește cu focus pe România"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up to src directory, then to instructions/web_search
        prompt_path = os.path.join(script_dir, "..", "instructions", "web_search", "system_prompt.txt")
        prompt_path = os.path.normpath(prompt_path)
        
        with open(prompt_path, "r", encoding="utf-8") as file:
            base_prompt = file.read().strip()
        return base_prompt
    except FileNotFoundError:
        print(f"❌ Eroare: Fișierul system_prompt.txt nu a fost găsit la {prompt_path}")
        print("Expected location: src/instructions/web_search/system_prompt.txt")
        return None
    
def enhance_user_query_for_romania(user_question):
    """Îmbunătățește cererea utilizatorului cu context românesc"""
    
    # Adaugă context românesc dacă nu este specificat deja
    romania_keywords = ['romania', 'romanian', 'romania', 'bucuresti', 'bucharest', 'timisoara', 'cluj', 'constanta', 'brasov', 'iasi']
    has_romania_context = any(keyword in user_question.lower() for keyword in romania_keywords)
    
    if not has_romania_context:
        enhanced_query = f"{user_question}"
    else:
        enhanced_query = user_question
    
    return enhanced_query

def save_results_to_file(user_question, enhanced_query, response_content, search_config, filename=None):
    """Salvează rezultatele căutării într-un fișier text cu metadate îmbunătățite"""
    if filename is None:
        filename = create_filename_from_question(user_question)
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write("="*80 + "\n")
        file.write("REZULTATE CĂUTARE PERPLEXITY AI - FOCUS PE ROMÂNIA\n")
        file.write("="*80 + "\n\n")
        file.write(f"Întrebarea originală: {user_question}\n")
        file.write(f"Cererea îmbunătățită: {enhanced_query}\n")
        file.write(f"Data căutării: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"Data de referință: {CURRENT_DATE}\n")
        file.write(f"Model: sonar-pro\n")
        file.write("-"*80 + "\n\n")
        file.write("FILTRE API DE CĂUTARE APLICATE:\n")
        file.write(f"📅 Interval de date: {search_config['search_after_date_filter']} până la {search_config['search_before_date_filter']}\n")
        file.write(f"🇷🇴 Locație: România (RO)\n")
        if search_config['web_search_options']['user_location'].get('latitude'):
            lat = search_config['web_search_options']['user_location']['latitude']
            lon = search_config['web_search_options']['user_location']['longitude']
            file.write(f"📍 Coordonate: {lat}, {lon}\n")
        file.write("-"*80 + "\n\n")
        file.write("REZULTATELE CĂUTĂRII:\n")
        file.write("-"*20 + "\n")
        file.write(response_content)
        file.write("\n\n" + "="*80 + "\n")
        file.write("REZUMATUL CONFIGURAȚIEI DE CĂUTARE:\n")
        file.write("- Restricție geografică: România (RO) prin filtrul de locație API\n")
        file.write("- Restricție temporală: 2005-2025 prin filtrele de interval de date API\n")
        file.write("- Prioritatea surselor: Guvern românesc > Instituții românești > Surse românești recente\n")
        file.write("- Filtrele API asigură returnarea doar a surselor românești și recente\n")
        file.write("="*80 + "\n")
    
    return filename

def search_with_perplexity_romania(
    query: str, 
    city_hint: str = "timisoara",
    model: str = "sonar-reasoning-pro",
    temperature: float = 0.1,
    max_tokens: int = 10000,
    search_context_size: str = "high",
    search_after_date: str = "1/1/2005",
    search_before_date: str = "5/30/2025"
) -> str:
    """
    Căutare inteligentă pentru România cu Perplexity API, optimizată pentru proceduri administrative
    
    Args:
        query: Întrebarea utilizatorului
        city_hint: Orașul de referință (timisoara, bucuresti, etc.)
        model: Modelul Perplexity de utilizat (sonar-reasoning-pro, sonar-pro, etc.)
        temperature: Controlează randomness-ul (0.0-1.0, mai mic = mai focusat)
        max_tokens: Numărul maxim de tokens pentru răspuns
        search_context_size: Amploarea căutării (low/medium/high)
        search_after_date: Caută conținut publicat după această dată (format: M/D/YYYY)
        search_before_date: Caută conținut publicat înainte de această dată (format: M/D/YYYY)
    
    Returns:
        Răspunsul structurat cu instrucțiuni pas cu pas
    """
    
    if not PERPLEXITY_API_KEY:
        print("❌ Eroare: PERPLEXITY_API_KEY nu a fost găsită în variabilele de mediu")
        return None
    
    # Încarcă prompt-ul de sistem
    system_prompt = load_system_prompt()
    if not system_prompt:
        return None
    
    location_filter = {"country": "RO", "city": city_hint}
    
    print(f"\n🔧 Configurație Perplexity:")
    print(f"   Model: {model}")
    print(f"   Temperature: {temperature}")
    print(f"   Max Tokens: {max_tokens}")
    print(f"   Context Size: {search_context_size}")
    print(f"   Search Date Range: {search_after_date} - {search_before_date}")
    print(f"   Location Filter: {city_hint}, Romania")
    print(f"\n📍 Căutare optimizată pentru: {city_hint}, Romania")
    print(f"🔍 Query: {query}")
    
    # Prepare the request headers
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prepare the request payload
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user", 
                "content": query
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "search_after_date_filter": search_after_date,
        "search_before_date_filter": search_before_date,
        "web_search_options": {
            "user_location": location_filter,
            "search_context_size": search_context_size
        }
    }
    
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data and response_data.get("choices") and len(response_data["choices"]) > 0:
                content = response_data["choices"][0]["message"]["content"]
                return content
            else:
                print("⚠️ Nu s-a primit răspuns valid de la Perplexity")
                return None
        else:
            print(f"❌ Eroare API Perplexity - Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Eroare la căutarea cu Perplexity: {e}")
        return None

if __name__ == "__main__":
    # Exemplu de utilizare - întrebările specifice României funcționează cel mai bine
    user_question = "Trebuie sa platesc parcarea pe strada Daliei, daca da cat ma costa si cum o platesc?"
    #"Ce documente îmi trebuie și unde trebuie să merg să îmi înnoiesc buletinul în Timișoara?"
    
    # Mai multe exemple pentru contextul românesc:
    # user_question = "Cum să îmi înregistrez noua adresă în Timișoara?"
    # user_question = "Pașii pentru a obține permis de conducere în România"
    # user_question = "Termenele și cerințele pentru declarația de impozit românească"
    # user_question = "Unde să obțin certificat de naștere în București?"
    
    # Opțional: Fă-l interactiv
    # user_question = input("Introdu întrebarea ta (va fi îmbunătățită pentru contextul românesc): ")
    
    # Opțional: Specifică un oraș românesc pentru filtrarea mai precisă a locației
    city_hint = "timisoara"  # Va folosi coordonatele Timișoarei dacă sunt detectate în cerere
    
    # Opțional: Specifică numele fișierului de ieșire (dacă None, se va auto-genera din întrebare)
    output_file = None  # Va auto-genera numele fișierului din întrebare și timestamp
    
    search_with_perplexity_romania(user_question, output_file, city_hint)