#! c:/Users/L170489/AppData/Local/Programs/Python/Python37/python
import typer
from sys import exit
import os
import subprocess
from console import console
import pathlib

app = typer.Typer()

# TODO create package


@app.command()
def go(path: str):

    try:
        f = open("nav.conf", "r")
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
        out_path = search[int(selection)]
    else:
        out_path = search[0]

    # Flatten and clean path string for new lines
    out_path = out_path.replace("\n", "")

    typer.launch(out_path)
    # if "ix" in os.name:
    #     # Replace home shortcut with home
    #     out_path = out_path.replace("~", os.getenv("HOME"))
    #     subprocess.run(["xdg-open", out_path])  # replace with path var
    # else:
    #     typer.launch(out_path)  # I think I can replace above with this command


@app.command()
def add():  # add global flag here?
    console.print("Add paths to nav file", style="magenta", justify="left")
    console.print(
        "These paths can be accessed with `nav go -path`", style="green", justify="left"
    )  # make nicer??

    # Get path of file being run
    filepath = pathlib.Path(__file__).parent.resolve()
    if not os.path.exists(os.path.join(filepath, "nav.conf")):
        pathlib.Path(os.path.join(filepath, "nav.conf")).touch()

    filepath = pathlib.Path(str(filepath) + "/nav.conf")
    print(os.name)
    print(filepath)
    if "ix" in os.name:
        subprocess.run(["xdg-open", filepath])
    else:
        # typer.launch(filepath, )
        os.system(f"Code {filepath}")
        # os.startfile(filepath)


if __name__ == "__main__":
    app()
    # go(path="af") # for debugging
