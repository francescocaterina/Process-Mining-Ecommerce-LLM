import streamlit as st
import pandas as pd
import pm4py
import os
from groq import Groq
from pm4py.algo.filtering.log.attributes import attributes_filter

# --- 1. CONFIGURAZIONE ---
os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin'
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="Process Mining AI Dashboard", layout="wide")

# --- 2. ELABORAZIONE E VALUTAZIONE (Discovery & Evaluation) ---
@st.cache_resource
def process_data():
    # Caricamento del log pre-elaborato [cite: 10, 12]
    df = pd.read_csv('cleaned_event_log.csv')
    df['time:timestamp'] = pd.to_datetime(df['time:timestamp'])
    log = pm4py.format_dataframe(df, case_id='case:concept:name',
                                 activity_key='concept:name',
                                 timestamp_key='time:timestamp')
    results = {}

    # Funzione per calcolare le 4 metriche di qualità
    def get_metrics(net, im, fm, log_data):
        fit = pm4py.conformance.fitness_token_based_replay(log_data, net, im, fm)['log_fitness']
        prec = pm4py.conformance.precision_token_based_replay(log_data, net, im, fm)
        gen = pm4py.algo.evaluation.generalization.algorithm.apply(log_data, net, im, fm)
        # Semplicità basata sulla struttura del grafo [cite: 17]
        simplicity_val = 1 / (len(net.places) + len(net.transitions) + len(net.arcs))
        return fit, prec, gen, simplicity_val

    # ALPHA MINER
    net_a, im_a, fm_a = pm4py.discover_petri_net_alpha(log)
    pm4py.save_vis_petri_net(net_a, im_a, fm_a, 'alpha_petri.png')
    f_a, p_a, g_a, s_a = get_metrics(net_a, im_a, fm_a, log)
    results['Alpha'] = {'fit': f_a, 'prec': p_a, 'gen': g_a, 'simp': s_a, 'img': 'alpha_petri.png'}

    # HEURISTIC MINER
    heu_net = pm4py.discover_heuristics_net(log)
    net_h, im_h, fm_h = pm4py.convert_to_petri_net(heu_net)
    pm4py.save_vis_petri_net(net_h, im_h, fm_h, 'heuristic_petri.png')
    f_h, p_h, g_h, s_h = get_metrics(net_h, im_h, fm_h, log)
    results['Heuristic'] = {'fit': f_h, 'prec': p_h, 'gen': g_h, 'simp': s_h, 'img': 'heuristic_petri.png'}

    # INDUCTIVE MINER
    tree_i = pm4py.discover_process_tree_inductive(log)
    net_i, im_i, fm_i = pm4py.convert_to_petri_net(tree_i)
    pm4py.save_vis_petri_net(net_i, im_i, fm_i, 'inductive_petri.png')
    f_i, p_i, g_i, s_i = get_metrics(net_i, im_i, fm_i, log)
    results['Inductive'] = {'fit': f_i, 'prec': p_i, 'gen': g_i, 'simp': s_i, 'img': 'inductive_petri.png'}

    return results, df

metrics_results, raw_df = process_data()

# --- 3. UI: MODELLI E METRICHE ---
st.title("📊 Process Mining Dashboard & AI Prediction")
st.markdown("Analisi comparativa dei modelli scoperti ed engine predittivo[cite: 26, 27].")

cols = st.columns(3)
for i, (algo, data) in enumerate(metrics_results.items()):
    with cols[i]:
        st.header(f"Algoritmo: {algo}")
        st.metric("Fitness", f"{data['fit']:.2f}")
        st.metric("Precision", f"{data['prec']:.2f}")
        st.metric("Simplicity", f"{data['simp']:.4f}")
        st.image(data['img'], caption=f"Petri Net - {algo}")

# --- 4. NUOVA SEZIONE: PREDICTION ---
st.divider()
st.subheader("🔮 Next Event Prediction")
st.write("Inserisci una sequenza di attività per prevedere la mossa successiva dell'utente.")

# Selezione attività dal dataset
activities = raw_df['concept:name'].unique().tolist()
selected_path = st.multiselect("Seleziona il percorso attuale dell'utente:", options=activities)

if st.button("Esegui Predizione"):
    if selected_path:
        # Calcolo statistico della prossima attività più probabile
        # Cerchiamo nei dati reali quali attività seguono l'ultima selezionata
        last_activity = selected_path[-1]
        transitions = raw_df.shift(-1)[raw_df['concept:name'] == last_activity]['concept:name'].value_counts()

        most_likely = transitions.idxmax() if not transitions.empty else "Fine Sessione"

        # Chiediamo all'AI di interpretare il risultato [cite: 20]
        pred_prompt = f"""
        L'utente ha seguito questo percorso: {' -> '.join(selected_path)}.
        Statisticamente, l'evento successivo più frequente nel log è: {most_likely}.
        
        Come esperto di Process Mining, analizza:
        1. Perché questa predizione è sensata in un contesto E-commerce?
        2. Quale azione di business suggeriresti per aumentare la conversione in questo punto?
        """

        with st.spinner("Analisi predittiva in corso..."):
            pred_res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": pred_prompt}]
            )
            st.success(f"**Prossima attività predetta: {most_likely}**")
            st.info(pred_res.choices[0].message.content)
    else:
        st.warning("Seleziona almeno un'attività per generare una previsione.")

# --- 5. REASONING & ANOMALIES ---
st.divider()
st.subheader("💬 AI Analyst - Anomalie e Ottimizzazione")

context = "Metriche correnti:\n"
for algo, data in metrics_results.items():
    context += f"- {algo}: Fit {data['fit']:.2f}, Prec {data['prec']:.2f}, Simp {data['simp']:.4f}\n"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": f"Sei un consulente di Process Mining. Analizza i dati: {context}. Trova colli di bottiglia e anomalie[cite: 22, 29]."}
    ]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

if chat_input := st.chat_input("Esempio: Quale modello è più affidabile per trovare colli di bottiglia?"):
    st.session_state.messages.append({"role": "user", "content": chat_input})
    with st.chat_message("user"): st.markdown(chat_input)

    with st.chat_message("assistant"):
        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.messages)
        ans = completion.choices[0].message.content
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
