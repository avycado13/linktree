.PHONY: build serve format lock

build:
	uv run build.py
	uv run pagefind --site dist
serve:
	uv run python -m http.server 8080 --directory dist
format:
	uv run ruff format
lock:
	uv lock