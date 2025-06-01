# AI Agent Settings - Ghid de Utilizare

## Cum să configurezi modelele pentru fiecare tool

### Accesarea Settings-urilor

1. **Deschide AI Agent**: Navighează la secțiunea AI Agent din aplicație
2. **Click pe "Settings"**: În colțul din dreapta sus al header-ului AI Agent
3. **Se deschide modalul de configurări** cu 5 tab-uri pentru fiecare tool

### Tools Disponibile și Modelele Lor

#### 1. **Query Reformulation** 🔄
- **Funcție**: Îmbunătățește întrebările utilizatorilor pentru căutări mai bune
- **Modele disponibile**: Gemini (2.0-flash-exp, 2.5-flash-exp, 2.5-pro-exp, etc.)
- **Recomandat**: `gemini-2.5-pro-exp` pentru reformulări mai inteligente

#### 2. **TimPark Payment** 🚗  
- **Funcție**: Automatizează plata parcării în Timișoara
- **Modele disponibile**: Gemini
- **Recomandat**: `gemini-2.5-flash-exp` pentru viteză și acuratețe

#### 3. **Web Search** 🌐
- **Funcție**: Caută informații pe website-uri românești 
- **Modele disponibile**: Perplexity (sonar-reasoning-pro, sonar-pro, etc.)
- **Recomandat**: `sonar-reasoning-pro` pentru cercetare avansată

#### 4. **Trusted Sites Search** 🏛️
- **Funcție**: Caută doar pe site-uri guvernamentale oficiale
- **Modele**: MIXT - Gemini pentru selecția domeniilor + Perplexity pentru căutare
- **Recomandat**: 
  - Gemini: `gemini-2.5-flash-exp`
  - Perplexity: `sonar-reasoning-pro`

#### 5. **Final Response Generation** ✨
- **Funcție**: Sintetizează toate rezultatele într-un răspuns final
- **Modele disponibile**: Gemini  
- **Recomandat**: `gemini-2.5-pro-exp` pentru răspunsuri complete

### Parametri Configurabili

Pentru fiecare tool poți seta:

- **Model**: Alege din lista de modele disponibile
- **Temperature** (0.0 - 1.0): 
  - 0.0-0.3 = Mai concentrat și consistent
  - 0.4-0.7 = Echilibrat  
  - 0.8-1.0 = Mai creativ și variat
- **Max Tokens**: Numărul maxim de tokeni pentru răspuns

### Configurații Recomandate per Scenarii

#### Pentru Informații Oficiale (Taxe, Proceduri)
```
Query Reformulation: gemini-2.5-pro-exp, temp=0.1
TimPark Payment: gemini-2.5-flash-exp, temp=0.1  
Web Search: sonar-reasoning-pro, temp=0.1
Trusted Sites: gemini-2.5-flash-exp + sonar-reasoning-pro, temp=0.1
Final Response: gemini-2.5-pro-exp, temp=0.1
```

#### Pentru Răspunsuri Creative (Idei, Sugestii)
```
Query Reformulation: gemini-2.5-pro-exp, temp=0.3
TimPark Payment: gemini-2.5-flash-exp, temp=0.1 (rămâne precis)
Web Search: sonar-reasoning-pro, temp=0.2
Trusted Sites: gemini-2.5-flash-exp + sonar-reasoning-pro, temp=0.2  
Final Response: gemini-2.5-pro-exp, temp=0.4
```

#### Pentru Viteză Maximă
```
Toate: Modele *-flash-exp cu temperature=0.1 și max_tokens redus
```

### Salvarea și Persistența

- **Salvare**: Click pe "Save Changes" pentru a aplica configurațiile
- **Persistență**: Configurările se salvează în localStorage și pe server
- **Reset**: "Reset" pentru a reveni la ultima salvare
- **Defaults**: Aplicația vine cu configurații optime pre-setate

### Testarea Configurațiilor

După salvare, testează cu întrebări relevante:
- "taxe locuinta Timisoara" → Vezi cum funcționează trusted sites search
- "platesc parcarea 2 ore" → Testează TimPark automation
- "certificat urbanism" → Verifică web search și final response

### Tips & Tricks

1. **Pentru început**: Folosește configurațiile default - sunt optimizate
2. **Experimentează gradually**: Schimbă un singur parametru odată
3. **Temperature mai mică** pentru informații factuale
4. **Temperature mai mare** pentru brainstorming și creativitate  
5. **Modele Pro** pentru task-uri complexe, **Flash** pentru viteză
6. **Max tokens** mai mult pentru răspunsuri detaliate

Configurațiile tale sunt salvate automat și vor fi utilizate pentru toate întrebările viitoare! 🎯 