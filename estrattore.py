import urllib.request
import csv
import io
from html.parser import HTMLParser

class FCIParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self.current_race = {"luogo": "", "data": ""}
        self.in_info_block = False
        self.in_table_cell = False
        self.temp_row = []
        self.current_data_line = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        # Identifica il blocco che contiene Data e Luogo
        if tag == "div" and "text-muted fs-5 mb-2" in attrs_dict.get("class", ""):
            self.in_info_block = True
            self.current_data_line = 0
        # Identifica le celle della tabella (Posizione, Nome, Squadra)
        if tag in ["th", "td"]:
            self.in_table_cell = True

    def handle_data(self, data):
        content = data.strip()
        if not content:
            return

        # Estrazione metadati della gara (Data e Luogo)
        if self.in_info_block:
            # La data è solitamente nella riga che contiene l'anno (es. 2026-03-01)
            if "202" in content and "-" in content:
                self.current_race["data"] = content.split(" - ")[0].strip()
            # Il luogo è spesso identificato dalle parentesi della provincia (es. (RA))
            elif "(" in content and ")" in content:
                self.current_race["luogo"] = content.strip()

        # Estrazione dati atleti
        if self.in_table_cell:
            self.temp_row.append(content)

    def handle_endtag(self, tag):
        if tag == "div":
            self.in_info_block = False
        if tag in ["th", "td"]:
            self.in_table_cell = False
        
        # Quando chiude la riga <tr>, salviamo i dati se abbiamo trovato un atleta
        if tag == "tr" and len(self.temp_row) >= 3:
            # Mappa dei dati:
            # temp_row[0] -> Posizione (es. 1°)
            # temp_row[1] -> Nome Corridore
            # temp_row[2] -> Squadra
            pos = self.temp_row[0]
            nome = self.temp_row[1]
            squadra = self.temp_row[2]
            
            self.results.append([
                nome, 
                squadra, 
                pos, 
                self.current_race["luogo"], 
                self.current_race["data"]
            ])
            self.temp_row = []

def main():
    url = "https://risultati-strada.federciclismo.it/risultati_gare_juniores.htm"
    # Se lo usi su Mac, cambia il percorso. Per GitHub Actions lascia solo il nome file.
    path_csv = "risultati_juniores.csv" 

    print(f"Download in corso da: {url}...")
    
    try:
        # User-agent per evitare blocchi base
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')

        parser = FCIParser()
        parser.feed(html)

        # Scrittura CSV con encoding ottimale per Excel (utf-8-sig)
        with open(path_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # Intestazione richiesta
            writer.writerow(["Nome", "Squadra", "Posizione", "Luogo", "Data"])
            writer.writerows(parser.results)

        print(f"Successo! Estratti {len(parser.results)} record nel file: {path_csv}")

    except Exception as e:
        print(f"Errore durante l'esecuzione: {e}")

if __name__ == "__main__":
    main()
