# FitBuddy — AI-Powered Diet & Meal Planner

FitBuddy is a Django-based web app that helps you plan meals, discover recipes, and track your daily progress. It includes an AI assistant powered by LangChain + Google Generative AI with a FAISS vector index for smart recipe retrieval and meal suggestions.


## Highlights

- Personalized meal plans and diet types (veg/non-veg, cuisines, etc.)
- Recipe browsing with images, ingredients, nutrition and instructions
- AI meal planning assistant using FAISS + embeddings (RAG)
- Daily progress, meal logs, and weight logs
- Clean, responsive UI with reusable templates and static assets


## Tech Stack

- Backend: Django 4.2, Django REST Framework (used internally)
- AI/RAG: LangChain, Google Generative AI Embeddings, FAISS
- Auth: Django (allauth/social-auth available in requirements)
- DB: SQLite (default), easily swappable
- Python: 3.12


## Project layout

Repository root (this folder):

- `requirements.txt` — Python dependencies
- `Smart_Diet_Planner/` — Django project folder containing:
	- `manage.py`
	- `FitBuddy/` (settings/urls)
	- `FitBuddy_app/` (core app: views, forms, templates, static)
	- `recipes/` (recipe models, views, RAG utilities, AI planner)
	- `diet_plan/` (diet plans and related views/templates)
	- `faiss_index.index/` (generated FAISS index directory; ignored by Git)
	- helper scripts: `regenerate_faiss.py`, `create_test_recipe.py`, `add_recipe_images.py`
- `.env.example` — environment variables template
- `.gitignore` — excludes secrets, media, db, and large generated files


## Quickstart (Windows PowerShell)

From the repo root (where `requirements.txt` lives):

```powershell
# 1) Create and activate a virtual environment
python -m venv .venv
. .\.venv\Scripts\Activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Create your .env from the example and edit values
Copy-Item .env.example .env -Force

# 4) Apply database migrations (run from the Django project folder)
cd Smart_Diet_Planner
python manage.py migrate

# 5) (Optional) Create an admin user
python manage.py createsuperuser

# 6) Build the FAISS index for the AI assistant (requires GOOGLE_API_KEY)
python regenerate_faiss.py

# 7) Start the development server
python manage.py runserver
```

Then open http://127.0.0.1:8000/ in your browser.


## Environment variables

Copy `.env.example` to `.env` and set values. Common variables:

- `DJANGO_SECRET_KEY` — required; any long random string in dev
- `DEBUG=1` — enable Django debug in development
- `ALLOWED_HOSTS=127.0.0.1,localhost` — comma-separated list
- `GOOGLE_API_KEY` — required for embeddings/FAISS (AI features)

Optional (only if you use them):
- `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY` — LangSmith tracing


## AI and FAISS index

The AI assistant uses a FAISS vector store built from your recipe data. If the index is missing or corrupted:

```powershell
cd Smart_Diet_Planner
python regenerate_faiss.py
```

The script will:
- read recipes from the database
- create embeddings via Google Generative AI
- save the FAISS index into `Smart_Diet_Planner/faiss_index.index/`

If you don’t set `GOOGLE_API_KEY`, the script will exit and explain what to do.


## Running tests

```powershell
cd Smart_Diet_Planner
python manage.py test
```


## Common tasks

- Collect static for production:
	```powershell
	cd Smart_Diet_Planner
	python manage.py collectstatic
	```

- Load or generate sample data: see helper scripts in `Smart_Diet_Planner/` such as `create_test_recipe.py` and `add_recipe_images.py`.


## Troubleshooting

- Git not found in PowerShell: install from https://git-scm.com/download/win or via `winget install --id Git.Git -e`.
- FAISS errors: ensure `GOOGLE_API_KEY` is set in `.env` and you have internet connectivity; then run `python regenerate_faiss.py` again.
- Database issues: delete `db.sqlite3` (if you’re okay losing local data) and re-run `python manage.py migrate`.
- Static files missing in production: run `python manage.py collectstatic` and configure your web server to serve `STATIC_ROOT`.


## Contributing

Issues and pull requests are welcome. Please open an issue to discuss substantial changes first.


## License

Add a license file (e.g., MIT/Apache-2.0) if you intend to open-source this project.
