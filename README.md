# ChaukaBartan

A Python webapp on AWS for task tracking, goal management, and habit improvement.

## Modules

- **Task Tracker** — daily/weekly tasks tied to hierarchical goals
- **Habit Tracker** — habit improvement following similar goal hierarchy

## Tech Stack

- **Backend:** Python (FastAPI)
- **Infrastructure:** AWS (ECS, RDS, VPC) via Terraform
- **Database:** PostgreSQL

## Project Structure

```
ChaukaBartan/
├── app/
│   ├── modules/
│   │   ├── task_tracker/    # Task & goal management
│   │   └── habits/          # Habit tracking
│   ├── api/                 # API routes
│   ├── models/              # Database models
│   └── core/                # Config, auth, shared utilities
├── infrastructure/
│   └── terraform/
│       ├── modules/         # Reusable Terraform modules
│       └── environments/    # dev / prod configs
└── tests/
    ├── unit/
    └── integration/
```

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
