import streamlit as st
import pandas as pd
import pm4py
import os
from groq import Groq

# --- 1. CONFIGURAZIONE ---
os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin'
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Process Mining Dashboard", layout="wide")

# --- 2. ELABORAZIONE E VALUTAZIONE (Fase: Discovery & Evaluation) ---
@st.cache_resource
def process_data():
    # Caricamento log (Fase: Preprocess Dataset)
    df = pd.read_csv('cleaned_event_log.csv')
    df['time:timestamp'] = pd.to_datetime(df['time:timestamp'])
    log = pm4py.format_dataframe(df, case_id='case:concept:name',
                                 activity_key='concept:name',
                                 timestamp_key='time:timestamp')

    results = {}

    # ALGORITMO 1: ALPHA MINER
    net_a, im_a, fm_a = pm4py.discover_petri_net_alpha(log)
    pm4py.save_vis_petri_net(net_a, im_a, fm_a, 'alpha.png')
    # Correzione nomi funzioni di valutazione
    fit_a = pm4py.conformance.fitness_token_based_replay(log, net_a, im_a, fm_a)
    prec_a = pm4py.conformance.precision_token_based_replay(log, net_a, im_a, fm_a)
    results['Alpha'] = {'fit': fit_a['log_fitness'], 'prec': prec_a, 'img': 'alpha.png'}

    # ALGORITMO 2: HEURISTIC MINER
    heu_net = pm4py.discover_heuristics_net(log)
    pm4py.save_vis_heuristics_net(heu_net, 'heuristic.png')
    net_h, im_h, fm_h = pm4py.convert_to_petri_net(heu_net)
    fit_h = pm4py.conformance.fitness_token_based_replay(log, net_h, im_h, fm_h)
    prec_h = pm4py.conformance.precision_token_based_replay(log, net_h, im_h, fm_h)
    results['Heuristic'] = {'fit': fit_h['log_fitness'], 'prec': prec_h, 'img': 'heuristic.png'}

    # ALGORITMO 3: INDUCTIVE MINER
    tree_i = pm4py.discover_process_tree_inductive(log)
    pm4py.save_vis_process_tree(tree_i, 'inductive.png')
    net_i, im_i, fm_i = pm4py.convert_to_petri_net(tree_i)
    fit_i = pm4py.conformance.fitness_token_based_replay(log, net_i, im_i, fm_i)
    prec_i = pm4py.conformance.precision_token_based_replay(log, net_i, im_i, fm_i)
    results['Inductive'] = {'fit': fit_i['log_fitness'], 'prec': prec_i, 'img': 'inductive.png'}

    return log, results

# Esecuzione calcoli
try:
    log, metrics_results = process_data()
except Exception as e:
    st.error(f"Errore durante l'elaborazione: {e}")
    st.stop()

# --- 3. DASHBOARD UI ---
st.title("📊 Process Mining Dashboard")

# Visualizzazione Metriche per Evaluation
st.subheader("Modelli e Metriche di Qualità")
col1, col2, col3 = st.columns(3)
for i, (algo, data) in enumerate(metrics_results.items()):
    with [col1, col2, col3][i]:
        st.info(f"Modello: **{algo}**")
        st.metric("Fitness", f"{data['fit']:.3f}")
        st.metric("Precision", f"{data['prec']:.3f}")
        st.image(data['img'], caption=f"Visualizzazione {algo}")

# --- 4. CHATBOT PER REASONING ---
st.divider()
st.subheader("💬 AI Analyst (Reasoning & Anomalies)")

# Contesto per Llama (Generazione report e anomalie) [cite: 21, 22]
context = "Dati di performance dei modelli:\n"
for algo, data in metrics_results.items():
    context += f"- {algo}: Fitness {data['fit']:.3f}, Precision {data['prec']:.3f}.\n"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": f"Sei un assistente per il Process Mining. Conosci questi risultati: {context}. Aiuta l'utente a identificare problemi, anomalie e ottimizzare il processo[cite: 22, 23]."}
    ]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if user_input := st.chat_input("Chiedimi un'analisi dei colli di bottiglia o delle anomalie..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
        )
        ans = completion.choices[0].message.content
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})