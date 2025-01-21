import logging
from jinja2 import Environment, FileSystemLoader
from db import Database
import shutil
import os
from pathlib import Path
import toml


# Configure logging
logging.basicConfig(
    filename="debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Initialize Jinja environment
env = Environment(loader=FileSystemLoader("src/templates"))
tag_template = env.get_template("tag_template.html")
link_template = env.get_template("link_page_template.html")
tag_index_template = env.get_template("tag_index_template.html")

logging.debug("Loading config file")
config = toml.load(Path("linktagger.toml"))
search_enabled = config.get("search", {}).get("enabled", False)
if config.get("db", {}).get("url"):
    db = Database(config["db"]["url"])
else:
    db = Database()


output_directory = Path(
    config["user"]["output_dir"] if config["user"]["output_dir"] else "dist/"
)
if os.path.exists(output_directory):
    shutil.rmtree(output_directory)

# Copy src/static to dist/.
shutil.copytree("src/static/", output_directory)

logging.info("Fetching all links from the database...")
links = db.get_links()
logging.info(f"Fetched {len(links)} links.")
logging.info("Fetching all tags from the database...")
tags = db.get_tags()
logging.info(f"Fetched {len(tags)} tags.")

link_snippets: list[str] = []
for link in links:
    logging.debug(f"Processing link: {link}")
    link_tags = db.get_tags_by_link(link)
    logging.debug(f"Tags for link {link}: {link_tags}")
    tag_list = "\n".join(
        f'            <li><a href="/tags/{tag}">{tag}</a></li>' for tag in link_tags
    )
    link_snippet = f"""
    <div class="link">
        <a href="{link}"><p>{link}</p></a>
        <ul>
{tag_list}
        </ul>
    </div>
    """
    link_snippets.append(link_snippet)


logging.info("Writing Link page")
link_page_content = link_template.render(
    links=link_snippets, search_enabled=search_enabled, tags=tags
)
links_path = os.path.join(
    output_directory,
    config["user"]["links_path"] if config["user"]["links_path"] else "index.html",
)
with open(links_path, "w") as f:
    f.write(link_page_content)


if not os.path.exists(os.path.join(output_directory, "tags")):
    os.makedirs(os.path.join(output_directory, "tags"), exist_ok=True)
tag_snippets: list[str] = []
for tag in tags:
    logging.debug(f"Processing tag: {tag}")
    tag_links = db.get_links_by_tag(tag)
    logging.debug(f"Links for tag {tag}: {tag_links}")

    # Render the tag template using Jinja
    tag_page_content = tag_template.render(
        tag=tag, links=tag_links, search_enabled=search_enabled, tags=tags
    )
    tag_path = os.path.join(output_directory, "tags", tag)
    os.makedirs(tag_path, exist_ok=True)
    print(tag_path)
    logging.info(f"Writing HTML file for tag {tag}...")
    with open(os.path.join(tag_path, "index.html"), "w") as f:
        f.write(tag_page_content)
        logging.info(f"HTML page for tag {tag} written successfully.")

tag_index_content = tag_index_template.render(tags=tags, search_enabled=search_enabled)
with open(os.path.join(output_directory, "tags", "index.html"), "w") as f:
    f.write(tag_index_content)
    logging.info("HTML page for tag index written successfully.")
