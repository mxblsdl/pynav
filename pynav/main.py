from typing import Optional
import typer
import os
import subprocess
from pathlib import Path
from rich import print
import re

app = typer.Typer()

# TODO move to other script
def select_prompt(r, text):
    [print(i, l) for i, l in enumerate(r)]
    selection = typer.prompt(text)
    return selection


@app.command()
def go(path: str):

    try:
        lines = (Path.home() / ".nav.conf").read_text().splitlines()
    except FileNotFoundError as err:
        print(str(err) + ": Populate with `nav add`")
        raise typer.Exit(1)

    search = list(filter(lambda l: path.lower() in l.lower(), lines))

    if len(search) > 1:
        selection = select_prompt(
            search, "More than one matching path found\n Select desired path"
        )
        out_path = search[int(selection)]
    else:
        out_path = search[0]

    # Flatten and clean path string for new lines
    out_path = Path(out_path).expanduser()

    typer.launch(str(out_path))


@app.command()
def add():  # add global flag here?
    print("[bold red]Add paths to nav file [/bold red] :emo:")
    print("[red]These paths can be accessed with `nav go -path`[/red]")

    # Get path of file being run
    config_file = Path.home() / ".nav.conf"

    if not Path.exists(config_file):
        Path(config_file).touch()
        # TODO populate with template

    if "ix" in os.name:
        subprocess.run(["xdg-open", config_file])
    else:
        # os.system(f"Code {config_file}")
        os.startfile(config_file)


@app.command("r")
# TODO add code option flag
def open_r_proj(
    proj: str = typer.Argument(""),
    code: Optional[bool] = typer.Option(default=None, flag_value="c")
    #     None, help="Show R Project Files", rich_help_panel="Features"
):

    # Find projects
    lines = (Path.home() / ".nav.conf").read_text().splitlines()
    # Filter out comments
    lines = [l for l in lines if not l.startswith("#")]
    # Find appropraite index
    idx = lines.index("[R Projects Folder]")
    parent_dir = lines[idx + 1 : idx + 2][0]

    # Find all projects
    rprojs = Path(parent_dir).expanduser().rglob("*.Rproj")

    # Build file path lists

    r_full = [r for r in rprojs]
    r_name = [r.name for r in r_full]

    r_dict = dict(zip(r_name, r_full))

    if not proj == "":
        # Match argument to list of projects
        r_tmp_dict = {k: v for (k, v) in r_dict.items() if proj in k}

        # Create selection if more than one
        if len(r_tmp_dict.values()) > 1:
            selection = select_prompt(
                r_tmp_dict.values(),
                "More than one matching path found\n Select desired path",
            )
            r_paths = list(r_tmp_dict.values())
            r_path = r_paths[int(selection)]

    else:
        selection = select_prompt(r_name, "All R Projects")
        # make selection
        r_paths = list(r_tmp_dict.values())
        r_path = r_paths[int(selection)]

    # Launch project
    if code:
        os.system(f"code {r_path.parent}")
        # subprocess.run(["code", r_path])
    else:
        subprocess.run(["xdg-open", r_path])


# open_r_proj("shi", True)
