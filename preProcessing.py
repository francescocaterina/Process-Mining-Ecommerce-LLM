import pandas as pd
import pm4py
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter

# 1. Caricamento del dataset
# Il file deve essere nella stessa cartella di preProcessing.py
file_path = 'events.csv'
print(f"Caricamento di {file_path} in corso...")
df = pd.read_csv(file_path)

# 2. Pulizia (Clean)
# Rimuoviamo righe dove manca la sessione (Case ID)
df = df.dropna(subset=['user_session'])

# Convertiamo il tempo in formato datetime standard
df['event_time'] = pd.to_datetime(df['event_time'])

# 3. Filtro (Filter)
# Data la dimensione del file (105MB), prendiamo le prime 5000 sessioni univoche
# per garantire che gli algoritmi Alpha e Inductive girino velocemente
unique_sessions = df['user_session'].unique()[:5000]
df_filtered = df[df['user_session'].isin(unique_sessions)].copy()

# 4. Ridenominazione per standard Process Mining
# Mappiamo le colonne del dataset Kaggle ai nomi richiesti dai tool [cite: 26, 27]
df_filtered = df_filtered.rename(columns={
    'user_session': 'case:concept:name',  # Case ID
    'event_type': 'concept:name',         # Activity
    'event_time': 'time:timestamp',       # Timestamp
    'user_id': 'org:resource'             # Resource
})

# 5. Ordinamento cronologico
df_filtered = df_filtered.sort_values(by=['case:concept:name', 'time:timestamp'])

# 6. Esportazione
# Salviamo il log pulito sia in CSV che in XES (formato standard ProM)
df_filtered.to_csv('cleaned_event_log.csv', index=False)

print("--- Preprocessing Completato ---")
print(f"Righe processate: {len(df_filtered)}")
print(f"Sessioni (Casi) estratti: {len(unique_sessions)}")
print("File creato: cleaned_event_log.csv")