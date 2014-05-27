OParl Validator
===============

Dieses Repository dient der Entwicklung eines API-Clients zur Überprüfung einer OParl-API.

Dabei sollen die [Schema-Definitionen](https://github.com/OParl/schema) berücksichtigt werden.
=======
# OParl Validator

## Running

```bash
python2.7 -S bootstrap.py
bin/buildout
```

## Bear in Mind

Start all Python files with this to facilitate the switch
to Python 3 and make things easier in general:
```python
# -*- encoding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
```

## Anforderungsliste


### Servereigenschaften

4.7.2: Bei Listen mit mehr als 100 Einträgen wird Paginierung empfohlen.
Bei einer Paginierung muss jede Seite (bis auf die letzte) gleich viele
und maximal 100 Einträge enthalten. Die Seiten müssen mit den in RFC5988
beschriebenen HTTP-Headern verlinkt werden. Jede Seite muss mit der jeweils
nächsten Seite verlinkt sein, optional darf sie auch mit der vorherigen,
ersten und letzten Seite verlinkt sein.
4.7.3: Falls eine Liste, die direkt als Wert in einem Objekt gespeichert ist,
mehr als 100 Einträge enthält, soll sie über eine eigene URL angeboten werden.

4.8: Ein Server soll die Feeds "Neue Objekte", "Geänderte Objekte" und
"Entfernte Objekte" anbieten. Die Feeds müssen umgekehrt chronologisch
sortiert sein und es ist empfohlen, dass sie mindestens einen Zeitraum
von 365 Tagen abdecken.
4.8.1.: Wenn ein neues Objekt erstellt wird, 
gilt es nicht als Änderung, es darf also nur im Feed "Neue Objekte"
erscheinen, Dopplungen sind nicht erlaubt.

4.9.1: HTTP-HEAD muss für alle Dateianfragen unterstüzt werden.
4.9.2: Bei einer Dateianfrage über die Download-URL muss der Server
einen Content-Disposition Header senden mit dem Typ "attachment" und
dem filename-Parameter. Der Dateiname soll das angefragte Dokument 
beschreiben (also nicht immer gleich sein). Es wir ein Dateinamen aus
ASCII Zeichen empfohlen. Bei einer Dateianfrage über die Zugriffs-URL
hingegen darf kein Content-Disposition Header mit Typ "attachment" gesendet
werden.
4.9.3 Generell muss bei Dateianfragen ein Last-Modified-Header mitgeschickt
werden, empfohlen sind die Header "Content-Length" und "ETag".
4.9.4 Es ist empfohlen "Conditional GET" mit den Parametern
If-Modified-Since und If-None-Match anzubieten.
(Nicht gut testbar: 4.9.5 Die OParl API muss Zustandslos sein.
Dateiurls müssen eindeutig bleiben und dürfen keine Sessioninformtionen
beinhalten.)
4.9.6 Beim Dateienzugriff darf mit einer Weiterleitung geantwortet
werden, je nach Situation mit Statuscode 301 oder 307, 4.9.7,
bei nicht mehr vorhandenen Datein soll mit 410 geantwortet werden.

4.11 Server sollen mindestens eines der Kompressionsverfahren gzip,
compress oder deflate unterstützen und verwenden, falls ein Client
mittels Accept-Encoding-Header diese anfragt. Bereits komprimierte
Dateien, wie PDF, dürfen immer in einer unkomprimierten HTTP-Antwort
übertragen werden.
4.12 Bei ungültigen Anfragen, sollen die entsprechenden HTTP 1.1
Statuscodes ausgegeben werden, unter anderem: "Bad Request",
"Not Found" oder "Method Not Allowed".
4.13: Folgende URL-Parameter sind reserviert und dürfen nicht in
der URL eines Dokuments/einer Liste benutzt werden:
callback, startdate, enddate

5.1.1: Es sollen Unicode Strings verwendet werden


### Dokumenteigenschaften

5.2.3 Name und NameLong dürfen nicht identisch sein

1. Backlinks sollten, sofern semantisch zwingened, zu dem richtigen Objekt
   zurückverweisen.
2. Die Felder `name` und `fileName` von `Document` sollen nicht identisch sein.
3. JSON-Objekte vom Typ `Location` können Namen und Geo-Koordinaten enthalten.
   Es gilt die Übereinstimmung dieser Daten zu validieren.
4. Auf jedem System muss genau ein Objekt vom Typ oparl:System verfügbar sein.
5. Elemente "rgs" eines oparl:Body sind zwölfstellig und können im Web nachgeschlagen werden.
6. Elemente "status" eines oparl:Person sollen, so vorhanden, die weibliche und die männliche Form des Wertes in genau dieser Reihenfolge enthalten.
7. Jedem Mitglied einer oparl:Oraganization soll ein Objekt oparl:Person zugehörig sein.
8. Elemente "post" eines oparl:Organization sollen, so vorhanden, die weibliche und die männliche Form des Wertes in genau dieser Reihenfolge enthalten.
