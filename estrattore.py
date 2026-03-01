import urllib.request
import csv
from html.parser import HTMLParser

class FCIParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self.current_race = {"luogo": "", "data": ""}
        self.in_info_block = False
        self.in_table_cell = False
        self.temp_row = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "div" and "text-muted fs-5 mb-2" in attrs_dict.get("class", ""):
            self.in_info_block = True
        if tag in ["th", "td"]:
            self.in_table_cell = True

    def handle_data(self, data):
        content = data.strip()
        if not content:
            return

        if self.in_info_block:
            if "202" in content and "-" in content:
                self.current_race["data"] = content.split(" - ")[0].strip()
            elif "(" in content and ")" in content:
                self.current_race["luogo"] = content.strip()

        if self.in_table_cell:
            self.temp_row.append(content)

    def handle_endtag(self, tag):
        if tag == "div":
            self.in_info_block = False
        if tag in ["th", "td"]:
            self.in_table_cell = False
        
        if tag == "tr":
            if len(self.temp_row) >= 3:
                pos = self.temp_row[0]
                nome = self.temp_row[1]
                squadra = self.temp_row[2]
                
                if nome.lower() != "corridore":
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
    path_csv = "risultati_juniores.csv" 

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')

        parser = FCIParser()
        parser.feed(html)

        # --- LOGICA DI ORDINAMENTO ---
        # Ordiniamo prima per Data (indice 4) e poi per Nome (indice 0)
        # In Python, sorted è stabile, quindi l'ordine secondario va messo per primo 
        # oppure si usa una lambda con più chiavi:
        risultati_ordinati = sorted(parser.results, key=lambda x: (x[0], x[4]))
        # -----------------------------

        with open(path_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["Nome", "Squadra", "Posizione", "Luogo", "Data"])
            writer.writerows(risultati_ordinati)

        print(f"Successo! {len(risultati_ordinati)} record ordinati per Nome e Data.")

    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    main()
