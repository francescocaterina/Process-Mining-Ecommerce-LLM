import pandas as pd
import pm4py
from groq import Groq
import os

# --- 1. CONFIGURAZIONE AI (LLAMA) ---
# Inserisci qui la tua chiave API di Groq
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# --- 2. ELABORAZIONE DATI CON PM4PY ---
print("Caricamento log e calcolo statistiche...")

try:
    # Caricamento del file
    df = pd.read_csv('cleaned_event_log.csv')
    df['time:timestamp'] = pd.to_datetime(df['time:timestamp'])

    # Estrazione delle varianti
    variants = pm4py.get_variants(df, activity_key='concept:name', case_id_key='case:concept:name')
    sorted_variants = sorted(variants.items(), key=lambda x: x[1], reverse=True)

    # Calcolo durata media
    case_durations = pm4py.get_all_case_durations(df, activity_key='concept:name',
                                                  case_id_key='case:concept:name',
                                                  timestamp_key='time:timestamp')
    avg_duration = sum(case_durations) / len(case_durations) if case_durations else 0

    # Prepariamo il riassunto per Llama
    top_variants_summary = ""
    for i, (variant, count) in enumerate(sorted_variants[:5]):
        path = " -> ".join(variant)
        top_variants_summary += f"{i+1}. {path} (Occorrenze: {count})\n"

    # --- 3. CREAZIONE DEL PROMPT ---
    prompt = f"""
    Sei un esperto analista di Process Mining. Analizza i dati estratti da un log E-commerce:
    
    STATISTICHE GENERALI:
    - Sessioni totali: {df['case:concept:name'].nunique()}
    - Durata media: {avg_duration:.2f} secondi
    
    TOP 5 PERCORSI (VARIANTI):
    {top_variants_summary}
    
    RICHIESTA:
    1. Fornisci un'analisi critica di questi percorsi.
    2. Identifica colli di bottiglia o problemi nella User Experience.
    3. Suggerisci una strategia di business basata su questi dati.
    """

    # --- 4. CHIAMATA A LLAMA ---
    print("Inviando i dati a Llama 3 via Groq...")

    chat_completion = client.chat.completions.create(
        # Modello Llama 3.3 (70 miliardi di parametri, molto preciso)
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Sei un analista dati specializzato in Process Mining e ottimizzazione processi aziendali."
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    print("\n" + "="*50)
    print("ANALISI STRATEGICA DI LLAMA 3 (VIA GROQ)")
    print("="*50)
    print(chat_completion.choices[0].message.content)
    print("="*50)

except FileNotFoundError:
    print("Errore: Assicurati che 'cleaned_event_log.csv' sia nella cartella.")
except Exception as e:
    print(f"Si è verificato un errore: {e}")