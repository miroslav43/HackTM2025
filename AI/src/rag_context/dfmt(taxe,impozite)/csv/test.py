import pandas as pd
import os

def extract_rag_context():
    csv_file = 'dfmt_pagini_continut_txt.csv'
    output_file = 'rag_dfmt_taxe_impozite.txt'
    
    try:
        df = pd.read_csv(csv_file)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Informații despre impozite și taxe locale din Municipiul Timișoara\n\n")      
            for index, row in df.iterrows():
                if pd.notna(row['rezumat']) and row['rezumat'].strip():
                    # Aplică filtrarea pentru a șterge "|" și "?>"
                    filtered_content = row['rezumat'].replace("|", "").replace("?>", "")
                    # Curăță spațiile multiple rezultate din filtrare
                    filtered_content = " ".join(filtered_content.split())
                    
                    f.write(f"**Conținut:** {filtered_content}\n")
        
        print(f"Context RAG generat cu succes în {output_file}")
        print(f"Total documente procesate: {len(df)}")
        
    except FileNotFoundError:
        print(f"Fișierul {csv_file} nu a fost găsit!")
    except Exception as e:
        print(f"Eroare: {e}")

if __name__ == "__main__":
    extract_rag_context()
