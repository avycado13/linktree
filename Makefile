.PHONY: format build lock serve

build:
	uv run cli.py bulkadd links.txt
	uv run build.py
	npx pagefind --site dist
serve:
	uv run python -m http.server 8080 --directory dist
format:
	uv run ruff format
lock:
	uv lock