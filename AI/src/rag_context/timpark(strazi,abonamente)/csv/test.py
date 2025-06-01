import pandas as pd
import os

def extract_rag_context():
    csv_file = 'timpark_timpark_ascii.csv'
    output_file = 'timpark_informatii_generale.txt'
    
    try:
        df = pd.read_csv(csv_file)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            
            for index, row in df.iterrows():
                if pd.notna(row['rezumat']) and row['rezumat'].strip():
                    f.write(f"## Pagina {index + 1}\n")
                    f.write(f"**Conținut:** {row['rezumat']}\n")
        
        print(f"Context RAG generat cu succes în {output_file}")
        print(f"Total documente procesate: {len(df)}")
        
    except FileNotFoundError:
        print(f"Fișierul {csv_file} nu a fost găsit!")
    except Exception as e:
        print(f"Eroare: {e}")

if __name__ == "__main__":
    extract_rag_context()
