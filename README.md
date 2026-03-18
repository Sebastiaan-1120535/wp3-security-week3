# Werkplaats 3 - Test-Correct

## Installatie

### Stap 1: Virtuele omgeving aanmaken

Maak een virtuele omgeving aan met het volgende commando:

```shell
python -m venv .venv
```

### Stap 2: Virtuele omgeving activeren

Activeer de virtuele omgeving:

```shell
.venv\Scripts\Activate.ps1
```

### Stap 3: Dependencies installeren

Installeer de vereiste libraries:

```shell
pip install Flask
```

## Opstart instructies

Start het project met het volgende commando:

```shell
py app.py
```

import json data via het volgende commando:
hierbij is de flag optioneel

```shell
py import_data.py <json_bestand> --cleanup
```
interface beschikbaar in het dashboard voor de docent


De applicatie is nu beschikbaar op: **http://localhost:5000**

## Inloggegevens

Gebruik de onderstaande credentials om in te loggen:

| Rol             | Email                           | Wachtwoord   |
| --------------- | -----------------               | ------------ |
| **Docent**      | docent.biologie@test.nl         | password     |
| **Docent**      | docent.natuurkunde@test.nl      | password     |
| **Docent**      | docent.scheikunde@test.nl       | password     |
| **Docent**      | docent.wiskunde@test.nl         | password     |
| **Student**     | sam@test.nl                     | password     |
| **Student**     | alex@test.nl                    | password     |
| **Student**     | jamie@test.nl                   | password     |
| **Student**     | taylor@test.nl                  | password     |
| **Student**     | robin@test.nl                   | password     |
| **Student**     | noah@test.nl                    | password     |
| **Student**     | emma@test.nl                    | password     |
| **Student**     | milan@test.nl                   | password     |
| **Student**     | lotte@test.nl                   | password     |
| **Student**     | daan@test.nl                    | password     |

# Bronnen

## Sjoerd
- https://sqlite.org/wal.html
- https://www.tencentcloud.com/techpedia/138374
- https://chatgpt.com/share/698c708a-82c4-800f-ab94-9579311f9253
- https://stackoverflow.com/questions/51081782/python-write-a-json-temporary-file-from-a-dictionary
- https://docs.python.org/3/library/tempfile.html
- 

## Roland
- Use JSDOC. (n.d.). https://jsdoc.app/tags-typedef
- Use JSDOC: Index. (n.d.). https://jsdoc.app/
- Stacked Bar Chart with Groups | Chart.js. (n.d.). https://www.chartjs.org/docs/latest/samples/bar/stacked-groups.html
- User. (2013b, januari 13). Convert Text to Numbers in SQLite. Stack Overflow. https://stackoverflow.com/a/14308502
- https://chatgpt.com/share/69b19728-96a4-8011-92b1-b9170f38bfe0
- User. (n.d.). Connecting points between missing data in chart.js. Stack Overflow. https://stackoverflow.com/questions/27107847/connecting-points-between-missing-data-in-chart-js
- https://chatgpt.com/share/69babd6e-d5c0-8011-a8c5-e33f9a3c1019
- Stacked bar/line | Chart.js. (n.d.). https://www.chartjs.org/docs/latest/samples/other-charts/stacked-bar-line.html

## Sebastiaan
- https://github.com/Rac-Software-Development/wp2-2025-mvc-1a1
We hebben de structuur van wp2 overgekopieerd naar dit project, vandaar ook de grootte "Big Bang" commit aan het begin van dit project.

- https://stackoverflow.com/questions/15181286/how-to-implement-an-endless-infinite-scroll-within-a-div-in-javascript-jquery