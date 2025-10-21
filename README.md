# Wstępne przetwarzanie i analiza danych pochodzących z turbin wiatrowych

Celem pracy jest implementacja metod przetwarzania danych SCADA pochodzących z turbin wiatrowych. W ramach przetwarzania danych zaimplementowane zostaną wybrane metody czyszczenia danych, analizy parametrów statystycznych oraz proste metody wykrywania anomalii. Dane analizowane w ramach projektu pochodzą ogólnodostępnych źródeł.


## Instrukcja uruchomienia
```bash
    # instalacja zależności
    pip install -r requirements.txt
```


## Wykorzystanie
Program pozwala na wskazanie ścieżki do folderu, w którym znajdują się pliki `.csv` zawierające dane dla kolejnych turbin. Po wczytaniu danych należy wskazać typ zestawu - Kelmarsh, Penmanshiel lub CareToCompare. Można także opcjonalnie wybrać, które parametry mają zostać załadowane wypisując je po przecinku w odpowiednim polu.

### Parametry do wyboru
Program pozwala na unifikację nazw sygnałów. Należy stworzyć słownik JSON, na podstawie którego będą modyfikowane nazwy sygnałów.


## Wspierane zestawy danych
- [Kelmarsh Farm](https://zenodo.org/records/5841834#.YgpBQ_so-V7)
- [Penmanshiel Farm](https://zenodo.org/records/5946808#.YgpAmvso-V5)
- [CareToCompare](https://data.niaid.nih.gov/resources?id=zenodo_10958774)
    - [CareToCompare Windfarm A](https://zenodo.org/records/14006163)
    - [CareToCompare Windfarm B](https://zenodo.org/records/14006163)
    - [CareToCompare Windfarm C](https://zenodo.org/records/14006163)
