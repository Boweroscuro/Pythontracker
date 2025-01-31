from flask import Flask, render_template, request, redirect, url_for, g
import json
from datetime import datetime

app = Flask(__name__)

def carica_dati(file_name):
    try:
        with open(file_name, 'r') as file:
            dati = json.load(file)
            print("Dati caricati:", dati)  # Aggiungi questa linea per il debug
            return dati
    except FileNotFoundError:
        print(f"Errore: il file {file_name} non è stato trovato.")
        return {"attività": []}
    except json.JSONDecodeError:
        print(f"Errore: il file {file_name} contiene dati non validi.")
        return {"attività": []}


# Funzione per salvare i dati nel file JSON
def salva_dati(file_name, dati):
    with open(file_name, 'w') as file:
        json.dump(dati, file, indent=4)

# Passiamo i punti totali a tutte le pagine tramite before_request
@app.before_request
def before_request():
    dati_utente = carica_dati('dati_utente.json')
    g.punti_totali = dati_utente.get("punteggio_totale", 0)  # Prende solo il punteggio

# Route per la home page
@app.route('/')
def home():
    dati_utente = carica_dati('dati_utente.json')
    return render_template('index.html', dati_utente=dati_utente)

@app.route('/attività')
def attività():
    attività_predefinite = carica_dati('attività_predefinite.json')
    
    # Debug per vedere cosa viene caricato
    print("Attività predefinite:", attività_predefinite)

    # Usa la chiave 'attivita' invece di 'attività'
    return render_template('attività.html', attività=attività_predefinite.get('attivita', []))

@app.route('/aggiungi_attività', methods=["POST"])
def aggiungi_attività():
    nome_attività = request.form['attività']

    # Carica le attività predefinite
    attività_predefinite = carica_dati('attività_predefinite.json')

    # Trova l'attività selezionata
    attività_selezionata = next((att for att in attività_predefinite["attivita"] if att["nome"] == nome_attività), None)

    if attività_selezionata:
        punti = attività_selezionata["punti"]

        # Carica il punteggio utente
        dati_utente = carica_dati('dati_utente.json')

        # Aggiorna i valori
        dati_utente["punteggio_totale"] += punti
        dati_utente["numero_attivita"] += 1

        # Salva i nuovi dati
        salva_dati('dati_utente.json', dati_utente)

        return redirect(url_for('home'))  # Ritorna alla home

    return "Attività non trovata!", 404


@app.route('/premi')
def premi():
    premi_disponibili = carica_dati('premi.json').get("premi", [])
    return render_template('premi.html', premi=premi_disponibili)


@app.route('/riscatta_premio', methods=["POST"])
def riscatta_premio():
    nome_premio = request.form['premio']
    
    # Carica i dati utente e premi
    dati_utente = carica_dati('dati_utente.json')
    premi_disponibili = carica_dati('premi.json').get("premi", [])

    # Trova il premio selezionato
    premio_selezionato = next((p for p in premi_disponibili if p["nome"] == nome_premio), None)

    if premio_selezionato:
        costo_premio = premio_selezionato["punti"]

        # Controlla se l'utente ha abbastanza punti
        if dati_utente.get("punteggio_totale", 0) >= costo_premio:
            # Sottrae i punti e salva
            dati_utente["punteggio_totale"] -= costo_premio
            salva_dati('dati_utente.json', dati_utente)
            return redirect(url_for('premi'))
        else:
            return "Punti insufficienti!", 400  # Errore se non ha abbastanza punti

    return "Premio non trovato!", 404  # Errore se il premio non esiste

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
