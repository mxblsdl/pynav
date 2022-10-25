from typing import Optional
import typer
import os
import subprocess
from pathlib import Path
from rich import print

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
def open_r_proj(
    proj: str = typer.Argument(""),
    code: Optional[bool] = typer.Option(default=False, flag_value="c")
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
    r_paths = [[r, r.name] for r in rprojs]

    if not proj == "":
        # Match argument to list of projects
        r_tmp_paths = [r for r in r_paths if proj in r[1]]

        # Create selection if more than one
        if len(r_tmp_paths) > 1:
            selection = select_prompt(
                [r[1] for r in r_tmp_paths],
                "More than one matching path found\n Select desired path",
            )
            r_path = r_tmp_paths[int(selection)]

    else:
        selection = select_prompt([r[1] for r in r_paths], "All R Projects")
        # make selection
        r_path = r_paths[int(selection)]

    # Launch project
    if code:
        os.system(f"code {r_path[0].parent}")
    else:
        subprocess.run(["xdg-open", r_path[0]])
