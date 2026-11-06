# AI instructions

Build **MediQuickV2 - Pharmacy Billing System** on top of this FastAPI + pytest starter. Read this whole file before
changing anything and follow it for every change.

## Project

MediQuick is a console-based pharmacy billing application for campus health store counter computers. It serves two types of users:
- Staff: Maintain the medicine inventory, add new medicines, update price and stock, and view stock status.
- Customers: Browse medicines, search items by name, add medicines to cart with prescription and stock checks, view/remove cart items, and place orders with printed bills containing flat 12% GST.
Data is persisted in medicines.csv across runs.


## Must have

- A REST API with validation and clear errors (400 for bad input, 404 for unknown ids)
- Tests for every service and endpoint
- Seed data for local runs

## Conventions

- Keep the existing folder structure
- One feature per commit, with conventional commit messages
- Keep README.md's run and test commands up to date

## Evolv platform rules — keep these working

- Stack: Python 3.12, FastAPI, pytest. Do not add other frameworks or services: grading runs with
  only this toolchain (evolv/python-3.12).
- Tests live under `tests/`. `.evolv/grade.yml` runs `pip install -q -r requirements.txt && python -m pytest -q --junitxml=reports/out.xml`
  and scores the JUnit XML it writes to `reports/*.xml` — keep it passing.
- `start.sh` must start the app on `$PORT`, and `GET /api/health` must answer 200:
  milestone API tests start the app that way and call it.
- Data: SQLite through SQLAlchemy. No external database.
