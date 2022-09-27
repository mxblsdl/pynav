#!/home/max/Documents/github/pynav/venv/bin/python3
import typer
from sys import exit
import os
import subprocess
from console import console
import pathlib

app = typer.Typer()


@app.command()
def go(path: str):

    try:
        f = open(".nav", "r")
    except FileNotFoundError as err:
        console.print(str(err) + ": Populate with `nav add`")
        exit(1)

    lines = f.readlines()

    search = list(filter(lambda l: path.lower() in l.lower(), lines))

    if len(search) > 1:
        [console.print(i, l) for i, l in enumerate(search)]
        selection = typer.prompt(
            f"More than one matching path found\n Select desired path"
        )
        out_path[selection]

    # Flatten and clean path string for new lines
    out_path = search[0]
    out_path = out_path.replace("\n", "")

    # TODO handle cases where more than one path are returned
    if "ix" in os.name:
        # Replace home shortcut with home
        out_path = out_path.replace("~", os.getenv("HOME"))
        subprocess.run(["xdg-open", out_path])  # replace with path var
    # TODO refine else process with windows
    else:
        subprocess.run(["explorer", "Documents"])  # replace with path var


@app.command()
def add():  # add global flag here?
    console.print("Add paths to nav file", style="magenta", justify="left")
    console.print(
        "These paths can be accessed with `nav go -path`", style="green", justify="left"
    )  # make nicer??

    # Get path of file being run
    filepath = pathlib.Path(__file__).parent.resolve()
    if not os.path.exists(os.path.join(filepath, ".nav")):
        pathlib.Path(os.path.join(filepath, ".nav")).touch()

    filepath = pathlib.Path(str(filepath) + "/.nav")
    subprocess.run(["xdg-open", filepath])


if __name__ == "__main__":
    app()
