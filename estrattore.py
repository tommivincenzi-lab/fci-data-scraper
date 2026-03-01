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
                
                # Salta la riga se è l'intestazione della tabella
                if nome.lower() != "corridore":
                    self.results.append([
                        nome, 
                        squadra, 
                        pos, 
                        self.current_race["luogo"], 
                        self.current_race["data"]
                    ])
            # Svuota sempre la riga alla fine del tag tr
            self.temp_row = []

def main():
    url = "https://risultati-strada.federciclismo.it/risultati_gare_juniores.htm"
    path_csv = "risultati_juniores.csv" 

    try:
        # User-Agent per evitare blocchi dal server
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')

        parser = FCIParser()
        parser.feed(html)

        # Scrittura del file CSV
        with open(path_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["Nome", "Squadra", "Posizione", "Luogo", "Data"])
            writer.writerows(parser.results)

        print(f"Successo! File '{path_csv}' aggiornato con {len(parser.results)} atleti.")

    except Exception as e:
        print(f"Errore durante l'estrazione: {e}")

# Questa riga è fondamentale per far girare lo script
if __name__ == "__main__":
    main()
