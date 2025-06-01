# TimPark Payment Tool Integration

## 📋 Prezentare Generală

Tool-ul TimPark Payment este o integrare avansată în sistemul Agent care permite automatizarea plății parcării în Timișoara. Tool-ul analizează inteligent intențiile utilizatorului și execută automat procesul de plată doar când detectează o intenție clară și explicită.

## 🏗️ Arhitectura Tool-ului

### Componente Principale

1. **`timpark_payment_tool.py`** - Modulul principal al tool-ului
2. **`completitions/timpark_autocomplete.py`** - Scriptul Selenium pentru automatizare
3. **`instructions/platire_timpark/system_prompt.txt`** - Instrucțiunile pentru analiza intenției

### Fluxul de Lucru

```
Query Utilizator
    ↓
Analiza Intenției (Gemini 2.5 Flash)
    ↓
Extragerea Parametrilor (durată)
    ↓
Decizia de Executare (da/nu)
    ↓
Automatizarea Plății (Selenium) - doar dacă intenția este clară
    ↓
Raportarea Rezultatelor
```

## ⚙️ Configurare

### 1. Configurația în `agent_config.json`

```json
{
    "timpark_payment": {
        "use_timpark_payment": true,
        "gemini_model": "gemini-2.5-flash-preview-05-20",
        "gemini_temperature": 0.1,
        "gemini_max_tokens": 1000,
        "output": {
            "save_to_file": true
        }
    }
}
```

### 2. Variabilele de Mediu

Asigurați-vă că aveți setată `GEMINI_API_KEY` în fișierul `.env`:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Dependințe Suplimentare

```bash
pip install selenium
```

Pentru automatizare, este necesar Chrome/Chromium:
- Chrome browser instalat
- ChromeDriver (gestionat automat de selenium 4.x)

## 🔍 Logica de Analiză a Intenției

### Criterii de Activare

Tool-ul se activează **DOAR** dacă:

1. **Intenția de Plată**: Utilizatorul exprimă explicit dorința de a plăti
   - ✅ "plateste parcarea"
   - ✅ "vreau să achit parcarea"
   - ❌ "cum platesc parcarea?" (întrebare informativă)

2. **Contextul Geographic**: 
   - ✅ "plateste parcarea în Timișoara"
   - ✅ "plateste parcarea" (implicit Timișoara)
   - ❌ "plateste parcarea în Cluj" (alt oraș)

3. **Extragerea Duratei**:
   - Valori permise: 30min, 1h, 1h 30min, ..., 12h
   - Mapare inteligentă: "o oră și jumătate" → "1h 30min"
   - Default: "1h" dacă nu se specifică

### Exemple de Procesare

| Query | Activare | Durată | Explicație |
|-------|----------|--------|------------|
| "plateste parcarea 2 ore" | ✅ | "2h" | Intenție clară + durată |
| "vreau să achit parcarea pentru 90 de minute" | ✅ | "1h 30min" | Intenție + conversie durată |
| "cum platesc parcarea?" | ❌ | "1h" | Întrebare informativă |
| "plateste parcarea în Cluj" | ❌ | "1h" | Alt oraș |
| "plateste parcarea 15 ore" | ✅ | "12h" | Intenție + limitare la maxim |

## 🚗 Automatizarea Selenium

### Funcționalitatea Scriptului

`timpark_autocomplete.py` execută următorii pași:

1. **Deschide browser-ul** (Chrome) și navigează la formularul TimPark
2. **Completează datele predefinite**:
   - Numărul de înmatriculare
   - Orașul (Timișoara)
   - Zona/Durata (setată dinamic din tool)
3. **Navighează prin paginile de plată**
4. **Completează datele de facturare** (predefinite)
5. **Ajunge la pagina finală de confirmare**

### Variabila Dinamică

Doar variabila `perioada_dorita` este setată dinamic de către tool:

```python
# Setat dinamic de tool
perioada_dorita = "2h"  # Extras din analiza intenției
```

### Date Predefinite

Scriptul folosește date predefinite pentru utilizatorul conectat:

```python
numar_masina = "TM99LAC"
oras_dorit = "Timisoara"
email_utilizator = "exemplu@domeniu.ro"
telefon_utilizator = "07xxxxxxxx"
# ... etc
```

## 📊 Integrarea în Agent

### Poziția în Workflow

Tool-ul TimPark este **Pasul 2** în workflow-ul agent-ului cu **logică condițională inteligentă**:

1. **Pasul 1**: Reformulare query (Gemini)
2. **Pasul 2**: **TimPark Payment Tool** 🆕
   - **DACĂ tool-ul se activează și execută plata** → **WORKFLOW SE OPREȘTE**
   - **DACĂ tool-ul NU se activează** → **continuă cu pașii următori**
3. **Pasul 3**: Căutare web regulată (Perplexity) - *doar dacă TimPark NU s-a executat*
4. **Pasul 4**: Căutare site-uri de încredere - *doar dacă TimPark NU s-a executat*
5. **Pasul 5**: Sinteză finală (Gemini 2.5 Flash) - *doar dacă TimPark NU s-a executat*

### Logica Condițională

```
Query Utilizator
    ↓
Pasul 1: Reformulare Query (opțional)
    ↓
Pasul 2: TimPark Payment Tool
    ↓
    ├── ACTIVAT + EXECUTAT? 
    │   ↓ DA
    │   📋 STOP WORKFLOW
    │   └── Salvare rezultate (doar pașii 1-2)
    │   
    └── NU ACTIVAT/EXECUTAT?
        ↓ DA  
        📋 CONTINUĂ WORKFLOW
        ├── Pasul 3: Web Search
        ├── Pasul 4: Trusted Sites
        ├── Pasul 5: Final Response
        └── Salvare rezultate complete (pașii 1-5)
```

### Avantajele Logicii Condiționale

1. **⚡ Eficiență Maximă**: Nu se pierde timp cu căutări web după ce plata e procesată
2. **🎯 Focalizare pe Acțiune**: Când utilizatorul vrea să plătească, se execută imediat
3. **💰 Reducerea Costurilor API**: Nu se fac apeluri inutile către Perplexity/Gemini
4. **🚀 Performanță Îmbunătățită**: Response time mai rapid pentru plăți parcare
5. **🧠 Logică Inteligentă**: Workflow-ul se adaptează automat la intenția utilizatorului

### Scenarii de Funcționare

| Tip Query | TimPark Activat | Pașii Executați | Rezultat |
|-----------|----------------|-----------------|----------|
| "plateste parcarea 2 ore" | ✅ DA | 1, 2 | Plată executată, workflow oprit |
| "cum platesc parcarea?" | ❌ NU | 1, 2, 3, 4, 5 | Informații complete despre plată |
| "reinoire buletin" | ❌ NU | 1, 2, 3, 4, 5 | Informații administrative complete |
| "plateste parcarea Cluj" | ❌ NU | 1, 2, 3, 4, 5 | TimPark nu suportă Cluj, căutări alternative |

### Rezultatele Tool-ului

Tool-ul returnează un dicționar cu:

```python
{
    "tool_enabled": bool,
    "user_query": str,
    "intent_analysis": {
        "activare_tool": bool,
        "numar_ore": str
    },
    "tool_activated": bool,
    "duration": str,
    "message": str,
    "automation_result": {  # doar dacă tool_activated = True
        "success": bool,
        "output": str,
        "error": str
    }
}
```

## 🧪 Testare

### Script de Test

Rulați `test_timpark_integration.py` pentru verificare:

```bash
python test_timpark_integration.py
```

### Test Manual

```python
from agent import Agent

agent = Agent("agent_config.json")
result = agent.process_query("plateste parcarea 2 ore", "test_timpark")

# Verificați rezultatul TimPark
timpark_result = result["timpark_payment_result"]
print(f"Tool activat: {timpark_result['tool_activated']}")
print(f"Durată: {timpark_result['duration']}")
```

## ⚠️ Considerații de Siguranță

1. **Execuția Condițională**: Automatizarea se execută DOAR la intenție explicită
2. **Validarea Datelor**: Toate intrările sunt validate și sanitizate
3. **Gestionarea Erorilor**: Erorile sunt capturate și raportate fără a afecta restul workflow-ului
4. **Timeout**: Scriptul Selenium are timeout de 5 minute
5. **Cleanup**: Fișierele temporare sunt șterse automat

## 🔧 Personalizare

### Modificarea Datelor Utilizatorului

Pentru a personaliza datele utilizatorului, editați variabilele din `timpark_autocomplete.py`:

```python
# Date personale
numar_masina = "TM99LAC"  # Modificați aici
email_utilizator = "email@domeniu.ro"  # Modificați aici
telefon_utilizator = "07xxxxxxxx"  # Modificați aici
# ... etc
```

### Ajustarea Zonelor de Parcare

Zona de parcare se poate ajusta prin modificarea variabilei:

```python
zona_dorita = "Timisoara Zona Autocare 12h - 15.00 LEI"  # Modificați aici
```

## 📝 Loguri și Debugging

Tool-ul oferă logging detaliat:

```
🔍 Analizez intenția utilizatorului pentru plata parcării...
✅ Tool activat! Execut automatizarea plății pentru 2h
🚗 Automatizare executată cu succes pentru 2h
```

Pentru debugging, verificați:
1. Fișierele de output în `results/agent_results/`
2. Logurile console ale agent-ului
3. Eventualele erori Selenium

## 🎯 Cazuri de Utilizare

### Scenarii Tipice

1. **Plată Rapidă**: "plateste parcarea 1 ora"
2. **Plată cu Durată Specifică**: "achita parcarea pentru 3 ore si jumate"
3. **Plată în Context**: "trebuie sa platesc parcarea pe strada Daliei"

### Scenarii care NU activează tool-ul

1. **Întrebări**: "cum platesc parcarea?"
2. **Alt oraș**: "plateste parcarea în București"
3. **Context nespecific**: "informații despre parcare"

## 🚀 Dezvoltare Viitoare

### Funcționalități Planificate

1. **Suport multi-oraș**: Extinderea pentru alte orașe din România
2. **Plăți recurente**: Automatizarea abonamentelor
3. **Integrare bancară**: Conectare directă cu API-uri bancare
4. **Notificări**: Alerte pentru expirarea parcării

### Contribuții

Pentru a contribui la dezvoltarea tool-ului:

1. Fork repository-ul
2. Creați o branch pentru feature-ul nou
3. Testați exhaustiv noua funcționalitate
4. Actualizați documentația
5. Creați un Pull Request

---

**🔗 Link-uri Utile:**
- [Documentația Agent System](../agent-system-overview.mdc)
- [Configurația Agent](../agent_config.json)
- [Scriptul de Test](../test_timpark_integration.py) 