import typer
import os
import subprocess
from pathlib import Path
from rich import print

app = typer.Typer()


@app.command()
def go(path: str):

    try:
        lines = (Path.home() / ".nav.conf").read_text().splitlines()
    except FileNotFoundError as err:
        print(str(err) + ": Populate with `nav add`")
        raise typer.Exit(1)

    search = list(filter(lambda l: path.lower() in l.lower(), lines))

    if len(search) > 1:
        [print(i, l) for i, l in enumerate(search)]
        selection = typer.prompt(
            f"More than one matching path found\n Select desired path"
        )
        out_path = search[int(selection)]
    else:
        out_path = search[0]

    # Flatten and clean path string for new lines
    out_path = Path(out_path).expanduser()

    typer.launch(str(out_path))


@app.command()
def add():  # add global flag here?
    print("[bold red]Add paths to nav file [/bold red] :boom:")
    print("[red]These paths can be accessed with `nav go -path`[/red]")

    # Get path of file being run
    config_file = Path.home() / ".nav.conf"

    if not Path.exists(config_file):
        Path(config_file).touch()

    if "ix" in os.name:
        subprocess.run(["xdg-open", config_file])
    else:
        # os.system(f"Code {config_file}")
        os.startfile(config_file)
