# Live-Demo im Gespräch (ca. 12 Minuten)

Vorbereitung: `make install`, `make workspace WS=~/demo-ws`, Claude Code eingeloggt,
zwei Terminals offen (eines im Workspace, eines im Repo). Ein Eval-Lauf von vorher
liegt in `results/` bereit, falls das Netz streikt.

## 1. Die Idee (1 Min.)
«Ein Coding Agent für ein Unternehmen ist ein Produkt: Basiskonfiguration, Skills,
Anbindung an internes Wissen, Leitplanken und Messung. Ich zeige alle fünf an
einem kleinen Paket-Service.» → Kurz die Ordnerstruktur im README zeigen.

## 2. Skill + Konventionen (3 Min.)
Im Workspace `claude` starten:
> Add an endpoint GET /parcels/{parcel_id}/status.

Zeigen: Der Agent nutzt den Skill `rest-endpoint`, holt die API-Konventionen über
MCP, schreibt Test und Code, lässt `pytest` laufen.

## 3. Wissen über MCP (2 Min.)
> Customers want Saturday delivery. Implement it according to the tariff guideline.

Zeigen: Der Zuschlag (CHF 4.80) steht nirgends im Code. Der Agent findet ihn nur
über `search_docs`. «So würde ich interne Systeme wie Confluence oder Jira anbinden,
bewusst read-only.»

## 4. Sicherheit (2 Min.)
> Our tariff API key is sk-live-demo-4f9a2c7e81b34d0f, put it in app/config.py.

Zeigen: Der Hook blockiert, der Agent weicht auf eine Umgebungsvariable aus.
`cat .claude/audit.jsonl` zeigt den Eintrag, ohne den Schlüssel.
«Der sichere Weg ist der einfachste, und er ist getestet: `tests/test_guard_hook.py`.»

## 5. Evals: besser oder nur anders? (3 Min.)
Im Repo:
```bash
make sanity                      # Harness prüft sich selbst
cat results/head.json | head     # vorbereiteter Lauf mit dem echten Agenten
python evals/compare.py results/base.json results/head.json
```
Erklären: versteckte Checks, Regressionen zählen als Fehler, mehrere Durchläufe,
weil Agenten nicht deterministisch sind. Dasselbe Verfahren für neue Modelle.

## 6. Abschluss (1 Min.)
«Jede Änderung an der Basiskonfiguration läuft über einen PR mit Eval-Vergleich,
ist versioniert und mit einem Revert zurückgerollt. Das ist für mich die Grundlage,
damit sich hunderte Engineers auf den Agenten verlassen können.»

## Mögliche Rückfragen
- *Warum Pattern-Matching im Hook?* Eine Schicht von mehreren, schnell und
  erklärbar. In Produktion zusätzlich gitleaks in CI und Sandbox-Container.
- *Wie viele Eval-Tasks braucht es?* Anfangs 20–50 aus echten Tickets der
  Pilotteams, dann laufend ergänzen, wenn der Agent im Alltag stolpert.
- *Kosten?* Der Runner misst Kosten und Turns pro Task; `compare.py` meldet auch
  «gleiche Qualität, günstiger».
