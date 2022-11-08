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

# TODO move to other script
def select_prompt(r, text):
    [print(i, l) for i, l in enumerate(r)]
    selection = typer.prompt(text)
    return selection


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
    elif len(search) == 0:
        print("Search does not match any paths\nCheck paths with `nav add()`")
        return
    else:
        out_path = search[0]

    # Flatten and clean path string for new lines
    out_path = Path(out_path).expanduser()

    typer.launch(str(out_path))


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
            """[paths]
# add each navigable path on a new line\n
[R Projects Folder]
# Should only contain one value
# Folder will be searched recursively"""
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
        elif len(r_tmp_paths) == 0:
            print(
                "No R projects match search :crying_face:\nCheck R folder with `nav add()`"
            )
            return
        else:
            r_path = r_tmp_paths[0]

    else:
        selection = select_prompt([r[1] for r in r_paths], "Choose from all R Projects")
        # make selection
        r_path = r_paths[int(selection)]

    # Launch project
    if code:
        os.system(f"code {r_path[0].parent}")
    else:
        typer.launch(str(r_path[0]), locate=True)
