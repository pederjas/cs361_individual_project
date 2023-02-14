CS361 Individual Project - Pet Finder


Get started:
clone repo
create a virtual environment: python -m venv venv
activate the virtual environment: source venv/bin/activate
install dependencies: pip install requirements.txt
create a file at the root of the project called: "google_api_key"



UML:
     ┌──────┐          ┌──────────┐          ┌────────────────┐
     │client│          │places_api│          │place_detail_api│
     └──┬───┘          └────┬─────┘          └───────┬────────┘
        │  http GET request │                        │         
        │ ──────────────────>                        │         
        │                   │                        │         
        │        JSON       │                        │         
        │ <─ ─ ─ ─ ─ ─ ─ ─ ─                         │         
        │                   │                        │         
        │              http GET request              │         
        │ ───────────────────────────────────────────>         
        │                   │                        │         
        │                   │JSON                    │         
        │ <─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─         
     ┌──┴───┐          ┌────┴─────┐          ┌───────┴────────┐
     │client│          │places_api│          │place_detail_api│
     └──────┘          └──────────┘          └────────────────┘

