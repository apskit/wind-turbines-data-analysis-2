# Wstępne przetwarzanie i analiza danych pochodzących z turbin wiatrowych

Celem pracy jest implementacja metod przetwarzania danych SCADA pochodzących z turbin wiatrowych. W ramach przetwarzania danych zaimplementowane zostaną wybrane metody czyszczenia danych, analizy parametrów statystycznych oraz proste metody wykrywania anomalii. Dane analizowane w ramach projektu pochodzą ogólnodostępnych źródeł.

## Wymagania
Python 3.10

## Instrukcja uruchomienia
```bash
    # instalacja zależności
    pip install -r requirements.txt
```


## Wykorzystanie
### Wczytywanie danych
Program pozwala na wskazanie ścieżki do folderu, w którym znajdują się pliki `.csv` zawierające dane z turbin. Po wczytaniu danych należy wskazać typ zestawu - Kelmarsh, Penmanshiel lub CareToCompare. Można także opcjonalnie wybrać, które parametry mają zostać załadowane wypisując je po przecinku w odpowiednim polu. Wczytywane dane są standaryzowane, a błędne wartości usuwane.

### Analiza danych
Po wczytaniu program pozwala na przeprowadzenie analizy danych po względem:
- dostępności:
    - liczba parametrów
    - procnt brakujących wartości
    - liczba datapoints
    - procent data uptime

- zakresów czasowych:
    - pierwszy timestamp
    - ostatni timestamp
    - częstotliwość próbkowania

- zakresów zmiennych:
    - zakresy wartości

### Wizualizacja
Program pozwala na generowanie wykresów:
    - dostępności danych w czasie
    - zakresu zmiennych - Boxplot/Histogram

### Parametry do wyboru
Program pozwala na unifikację nazw sygnałów. W tym celu należy umieścić w katalogu `config\signals_dict.json` słownik JSON, na podstawie którego będą modyfikowane nazwy sygnałów.

#### Przykładowy słownik JSON
```json
    {
        "kelmarsh": {
            "# Date and time": "timestamp",
            "Power (kW)": "power",
            "Wind speed (m/s)": "wind_speed",
        },
        "caretocompare": {
            "time_stamp": "timestamp",
            "asset_id": "turbine_id",
            "id": "record_id"    
        }
    }
```


## Wspierane zestawy danych
- [Kelmarsh Farm](https://zenodo.org/records/5841834#.YgpBQ_so-V7)
- [Penmanshiel Farm](https://zenodo.org/records/5946808#.YgpAmvso-V5)
- [CareToCompare](https://data.niaid.nih.gov/resources?id=zenodo_10958774)
    - [CareToCompare Windfarm A](https://zenodo.org/records/14006163)
    - [CareToCompare Windfarm B](https://zenodo.org/records/14006163)
    - [CareToCompare Windfarm C](https://zenodo.org/records/14006163)
