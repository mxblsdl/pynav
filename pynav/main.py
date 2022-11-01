from typing import Optional
import typer
import os
import subprocess
from pathlib import Path
from rich import print

app = typer.Typer(help="Navigate your R Projects and Folders", no_args_is_help=True)

# TODO move to other script
def select_prompt(r, text):
    [print(i, l) for i, l in enumerate(r)]
    selection = typer.prompt(text)
    return selection


# Set a default behavior if called without arguments
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Default Behaviour

    Args:
        ctx (typer.Context): These are other commands that can be passed to the tool
    """
    if ctx.invoked_subcommand is None:
        print(
            "Usage: Navigate to a set of predetermined folders or projects from the command line"
        )


@app.command()
def go(path: str = typer.Argument(default="")):
    """Open a folder, accepts partial matching

    Args:
        path (str, optional): Folder path to open. Searches from prepopulated list of destinations
    """
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
    """Opens a .nav.conf file to populate with folder paths"""
    print("[bold]Add paths to .nav.conf file [/bold] :white_check_mark:")
    print("[bold]Paths can be accessed with `nav go <path>`[/bold]")

    # Get path of file being run
    config_file = Path.home() / ".nav.conf"

    if not config_file.exists():
        config_file.touch()
        config_file.write_text(
            """[paths]
# add each navigable path on a new line\n
[R Projects Folder]
# Should only contain one value
# Folder will be searched recursively"""
        )

    if "ix" in os.name:
        subprocess.run(["xdg-open", config_file])
    else:
        # os.system(f"Code {config_file}")
        os.startfile(config_file)


@app.command("r")
def define_r_proj(
    proj: str = typer.Argument(""),
    code: bool = typer.Option(False, "--code", "-c", is_flag=True),
):
    """Open an R Project

    Args:
        proj (str, optional): Name of R Project. Supports partial matching.
        code (Optional[bool], optional): Should the folder be opened with VS Code
    """
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
            r_path = r_tmp_paths[0]

    else:
        selection = select_prompt([r[1] for r in r_paths], "All R Projects")
        # make selection
        r_path = r_paths[int(selection)]

    # Launch project
    if code:
        os.system(f"code {r_path[0].parent}")
    else:
        if "ix" in os.name:
            subprocess.run(["xdg-open", r_path[0]])
        else:
            os.startfile(r_path[0])
