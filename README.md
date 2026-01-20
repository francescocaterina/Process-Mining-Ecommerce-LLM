# Process Mining Model Evaluation Dashboard

Questo progetto si occupa della **valutazione oggettiva di modelli di Process Mining**, fornendo un set di strumenti per analizzare l'affidabilità e la qualità delle rappresentazioni ottenute dai log dei processi.

## 📌 Descrizione del Progetto

Il cuore della metodologia risiede nell'analisi quantitativa dei modelli attraverso lo script `dashboard.py`. Il sistema permette di confrontare diversi modelli estratti dai log, verificando quanto fedelmente rappresentino la realtà operativa documentata nei dati.

## 📊 Metodologie di Valutazione

Per determinare l'affidabilità dei modelli, vengono calcolate quattro metriche essenziali:

| Metrica | Descrizione | Obiettivo |
| :--- | :--- | :--- |
| **Fitness** | Capacità del modello di riprodurre le tracce del log. | Validità |
| **Precision** | Misura della specificità rispetto ai dati osservati. | Accuratezza |
| **Generalization** | Robustezza del modello su comportamenti futuri. | Predizione |
| **Simplicity** | Quantificazione della leggibilità strutturale del grafo. | Usabilità |

---

## 🚀 Installazione

1. **Clona il repository:**
   ```bash
   git clone [https://github.com/tuo-username/nome-repo.git](https://github.com/tuo-username/nome-repo.git)
   cd nome-repo
