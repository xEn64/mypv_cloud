# mypv_cloud

`mypv_cloud` ist eine Custom Integration für Home Assistant zur Nutzung der **my-PV Cloud-API**.

Die Integration dient dazu, Daten und Funktionen aus der Cloud-Anbindung von my-PV in Home Assistant verfügbar zu machen. Der Fokus liegt dabei nicht auf der lokalen Geräteschnittstelle, sondern auf der Anbindung der offiziellen Cloud-API.

# mypv_cloud

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=xEn64&repository=mypv_cloud&category=integration)

`mypv_cloud` ist eine Custom Integration für Home Assistant zur Nutzung der **my-PV Cloud-API**.

## Ziel der Integration

Dieses Add-on stellt eine Grundlage bereit, um Cloud-Daten von my-PV systematisch in Home Assistant einzubinden und für Automationen, Dashboards und Auswertungen nutzbar zu machen.

Geplant sind insbesondere folgende Funktionen:

- **Aktion zum Setzen von Leistung und Zeit**
  - Übergabe eines Leistungswerts
  - Übergabe einer Gültigkeitsdauer bzw. Laufzeit
  - Nutzung in Home-Assistant-Automationen zur gezielten Steuerung

- **Abruf von Vorhersagedaten**
  - Einbindung von Forecast-/Prognosedaten aus der my-PV Cloud
  - Bereitstellung der Werte als Sensoren bzw. auswertbare Entitäten in Home Assistant

## Funktionsumfang

Die Integration soll die my-PV Cloud-API nutzen, um:

- Cloud-Daten authentifiziert abzurufen
- relevante Mess- und Prognosewerte in Home Assistant bereitzustellen
- steuernde API-Funktionen als Aktionen/Services verfügbar zu machen

## Status

Das Projekt befindet sich im Aufbau und wird schrittweise erweitert.

Der aktuelle Entwicklungsstand konzentriert sich auf:

1. die Anbindung der Cloud-API
2. die Bereitstellung einer Aktion zum Setzen von Leistung und Zeit
3. die Integration von Vorhersagedaten

## Hinweis

Diese Integration ist für die **my-PV Cloud-API** vorgesehen.  
Sie ist damit von lokalen Integrationen für Geräte wie AC THOR oder andere lokale Netzwerkschnittstellen abzugrenzen.

alles mit chatgpt Erzeugt, läuft aber.