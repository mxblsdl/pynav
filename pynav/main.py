import typer
import os
from pathlib import Path
from rich import print
from itertools import chain

app = typer.Typer(
    help="Navigate your R Projects and Folders",
    epilog="Made for run with :snake:",
    rich_markup_mode="markdown",
    add_completion=False,
    no_args_is_help=True,
)


def select_prompt(r, text):
    [print(i, l) for i, l in enumerate(r)]
    selection = typer.prompt(text)
    return selection


def scan_dir(dir: list[str]) -> list[str]:
    projects = [
        [[p.path, p.name] for p in os.scandir(f) if os.path.isdir(p)] for f in dir
    ]
    # Flatten
    return list(chain.from_iterable(projects))


def find_paths(proj: str):
    """Open a folder, accepts partial matching

    Args:
        path (str, optional): Folder path to open. Searches from prepopulated list of destinations
    """
    try:
        lines = (Path.home() / ".nav.conf").read_text().splitlines()
    except FileNotFoundError as err:
        print(str(err) + ": Populate with `nav add`")
        raise typer.Exit(1)

    # Filter out comments
    lines = [l for l in lines if not l.startswith("#") or l == ""]

    # Find line with recursive keyword and select all lines before
    idx = lines.index("[recursive]")

    # Create a list of the single paths
    paths = lines[:idx]
    paths = [
        [str(Path(l).expanduser()), Path(l).name]
        for l in paths
        if not l.startswith("[")
    ]

    # Add recursive items to lines
    recursive_dirs = [
        Path(l).expanduser() for l in lines[idx:] if not l.startswith("[")
    ]

    if len(recursive_dirs) == 0:
        print("No recursive paths specified")

    r_paths = scan_dir(recursive_dirs)
    paths.extend(r_paths)

    if proj != "":
        # Match argument to list of projects
        tmp_paths = [p for p in paths if proj.lower() in p[1].lower()]

        # Create selection if more than one
        if len(tmp_paths) > 1:
            selection = select_prompt(
                [p[1] for p in tmp_paths],
                "More than one matching path found\n Select desired path",
            )
            return tmp_paths[int(selection)]

        if len(tmp_paths) == 0:
            print(
                "No projects match search :crying_face:\nCheck folders with `nav add()`"
            )
            raise typer.Exit(code=1)

        return list(*tmp_paths)

    # Select from all projects if nothing specified
    selection = select_prompt([p[1] for p in paths], "Choose from all Projects")
    return paths[int(selection)]


@app.command()
def go(
    proj: str = typer.Argument(default=""),
    code: bool = typer.Option(False, "--code", "-c", is_flag=True),
):
    path = find_paths(proj)

    if code:
        os.system(f"code {path[0]}")
        return None
    typer.launch(str(path[0]), locate=False)
    typer.Exit()


@app.command()
def add():  # add global flag here?
    """Opens a `.nav.conf` file to populate with folder paths"""
    print("[bold]Add paths to .nav.conf file [/bold] :white_check_mark:")
    print("[bold]Paths can be accessed with `nav go <path>`[/bold]")

    # Get path of file being run
    config_file = Path.home() / ".nav.conf"

    # I could replace this with a context manager for the file
    if not config_file.exists():
        config_file.touch()
        config_file.write_text(
            """[single paths]
# add each navigable path on a new line\n
[recursive]
# These folders will be searched recursively"""
        )
    typer.launch(str(config_file))
