import click
import loader as loader
from trogon import tui
import httpx
import prompts
from openai import OpenAI

# Load configuration
config = loader.load_config()

# Set up database connection
db = loader.load_db(config)


@tui()
@click.group()
def cli():
    pass


@cli.command("add")
@click.argument("url")
@click.option("--ai", is_flag=True)
@click.argument("tags", nargs=-1)  # Accept 0 or more tags
def add_link(url, tags, ai):
    """Add a link with tags."""
    tags = list(tags)
    if ai:
        if config["ai"]["enabled"]:
            ai_client = OpenAI(
                base_url=config["ai"]["url"],
                api_key=config["ai"]["api_key"] | "ollama",  # required, but unused
            )

            text = httpx.get(url=url)
            response = ai_client.chat.completions.create(
                model=config["ai"]["model"] | "o1",
                messages=prompts.gen_tags_prompt(text.text),
            )
            tags += list(response.choices[0].message.content)
        else:
            click.echo("AI not enabled in config file")
    db.insert_link_with_tags(url, list(tags))  # Convert tuple to list
    click.echo("Added link with tags!")


@cli.command("links")
def get_links():
    """Get all links in the database."""
    click.echo("Links in db")
    for link in db.get_links():
        click.echo(link)


@cli.command("tags")
def get_tags():
    """Get all tags in the database."""
    click.echo("Tags in db")
    for tag in db.get_tags():
        click.echo(tag)


@cli.command("strip")
@click.argument("file_path")
def parse_and_remove(file_path: str):
    """Remove everything before the first 'h' on each line in a file."""
    with open(file_path, "r") as infile:
        lines = infile.readlines()

    with open(file_path, "w") as outfile:
        for line in lines:
            # Find the first 'h' and keep everything after it
            modified_line = line.lstrip()
            if "h" in modified_line:
                # Keep everything after the first 'h'
                modified_line = modified_line[modified_line.index("h") :]
            outfile.write(modified_line)
    click.echo("Done!")


@cli.command("bulkadd")
@click.argument("file_path")
@click.option("--ai", is_flag=True)
def bulk_add_links(file_path: str, ai):
    """Bulk add links from a file, assuming format: 'url <tag1> <tag2> ...'"""
    with open(file_path, "r") as infile:
        lines = infile.readlines()

    for line in lines:
        # Split the line into URL and tags
        parts = line.split()
        if len(parts) > 0:
            url = parts[0]
            tags = parts[1:]  # Remaining parts are tags
            if ai:
                text = httpx.get(url=url)
                payload = {
                    "model": config["ai"]["model"],
                    "prompt": prompts.gen_tags_prompt(text.text),
                    "stream": False,
                    "keep_alive": "1m",
                    "format": {
                        "type": "object",
                        "properties": {"tags": {"type": "array"}},
                        "required": ["tags"],
                    },
                    "options": {
                        "temperature": 0.5,
                        "num_predict": 100,
                    },
                }
                response = httpx.post(config["ai"]["url"], json=payload)
                tags += httpx.Response.json(response)["tags"]
            db.insert_link_with_tags(url, tags)  # Directly insert into the database
    click.echo("Done!")


if __name__ == "__main__":
    cli()
