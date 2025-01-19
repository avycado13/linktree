.PHONY: build serve

build:
	uv run build.py
	uv run pagefind --site dist
serve:
	uv run python -m http.server 8080 --directory dist