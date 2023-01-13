import typer
import os
from pathlib import Path
from rich import print
from rich.progress import Progress, SpinnerColumn

app = typer.Typer(
    help="Navigate your R Projects and Folders",
    epilog="Made for run with :snake:",
    rich_markup_mode="markdown",
)


def select_prompt(r, text):
    [print(i, l) for i, l in enumerate(r)]
    selection = typer.prompt(text)
    return selection


@app.command()
def go(
    proj: str = typer.Argument(default=""),
    code: bool = typer.Option(False, "--code", "-c", is_flag=True),
):
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

    # Find appropriate index
    idx = lines.index("[recursive]")
    # Create a list of the single paths
    single_paths = lines[:idx]
    single_paths = [Path(l) for l in single_paths if not l.startswith("[")]

    # Create a
    single_paths = [[str(p.expanduser()), p.name] for p in single_paths]
    """I want to combine the recursive lines and the non recursive lines
    Need to separate out the recursive"""

    # Add recursive items to lines
    try:
        # ? This only allows for one value in the recursive section, should expand?? to more values??
        # parent_dir = lines[idx:][0]
        parent_dir = [l for l in lines[idx:] if not l.startswith("[")]
        parent_dir = Path(parent_dir[0]).expanduser()
        # Find all projects
        projects = [f.path for f in os.scandir(parent_dir) if f.is_dir()]

        # Build file path lists
        paths = [[p, Path(p).name] for p in projects]
        paths.extend(single_paths)
    except:
        print("No recursive paths specified")
        paths = single_paths

    # search = list(filter(lambda l: path.lower() in l.lower(), lines))
    if not proj == "":
        # Match argument to list of projects
        tmp_paths = [p for p in paths if proj.lower() in p[1].lower()]

        # Create selection if more than one
        if len(tmp_paths) > 1:
            selection = select_prompt(
                [p[1] for p in tmp_paths],
                "More than one matching path found\n Select desired path",
            )
            path = tmp_paths[int(selection)]
        elif len(tmp_paths) == 0:
            print(
                "No projects match search :crying_face:\nCheck folders with `nav add()`"
            )
            return
        else:
            path = tmp_paths[0]

    else:
        selection = select_prompt([p[1] for p in paths], "Choose from all Projects")
        # make selection
        path = paths[int(selection)]

    # Launch project
    if code:
        os.system(f"code {path[0]}")
    else:
        typer.launch(str(path[0]), locate=True)


@app.command()
def add():  # add global flag here?
    """Opens a `.nav.conf` file to populate with folder paths"""
    print("[bold]Add paths to .nav.conf file [/bold] :white_check_mark:")
    print("[bold]Paths can be accessed with `nav go <path>`[/bold]")

    # Get path of file being run
    config_file = Path.home() / ".nav.conf"

    if not config_file.exists():
        config_file.touch()
        config_file.write_text(
            """[single paths]
# add each navigable path on a new line\n
[recursive]
# These folders will be searched recursively"""
        )
    typer.launch(str(config_file))


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
    with Progress(SpinnerColumn(), transient=True) as progress:
        progress.add_task(description="Finding Files...")

        try:
            lines = (Path.home() / ".nav.conf").read_text().splitlines()
        except FileNotFoundError as err:
            print(str(err) + ": Populate with `nav add`")
            raise typer.Exit(1)

        # Filter out comments
        lines = [l for l in lines if not l.startswith("#")]
        # Find appropriate index
        idx = lines.index("[recursive]")
        # ? This only allows for one value in the recursive section, should expand?? to more values??
        parent_dir = lines[idx + 1 : idx + 2][0]

        # Find all projects
        projects = [f.path for f in os.scandir(parent_dir) if f.is_dir()]

        # Build file path lists
        paths = [[p, Path(p).name] for p in projects]

    if not proj == "":
        # Match argument to list of projects
        tmp_paths = [p for p in paths if proj in p[1]]

        # Create selection if more than one
        if len(tmp_paths) > 1:
            selection = select_prompt(
                [p[1] for p in tmp_paths],
                "More than one matching path found\n Select desired path",
            )
            path = tmp_paths[int(selection)]
        elif len(tmp_paths) == 0:
            print(
                "No projects match search :crying_face:\nCheck folders with `nav add()`"
            )
            return
        else:
            path = tmp_paths[0]

    else:
        selection = select_prompt([p[1] for p in paths], "Choose from all Projects")
        # make selection
        path = paths[int(selection)]

    # Launch project
    if code:
        os.system(f"code {path[0]}")
    else:
        typer.launch(str(path[0]), locate=True)
