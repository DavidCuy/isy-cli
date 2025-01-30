import os
from pathlib import Path
from typing import Optional

import typer


def validate_path_not_exist(*, path: Path, custom_error_message: Optional[str] = None, abort=True):
    """
    Validate that not exist a folder in case where path was found it raise a exception and abort the execution.
    :param path: A path for validate
    :param custom_error_message: A custom message, it show if an exception is raised.
    :return:
    """
    if path.exists():
        typer.echo(custom_error_message or f'Ya existe un archivo: {path}', color=typer.colors.RED)
        if abort:
            raise typer.Abort()
        return True
    return False


def validate_path_exist(*, path: Path, custom_error_message: Optional[str] = None):
    """
    Validate that exist a folder in case where path not found it raise a exception and abort the execution
    :param path: A path for validate
    :param custom_error_message: A custom message, it show if an exception is raised.
    :return:
    """
    if not path.exists():
        typer.echo(custom_error_message or f'Not exist the path: {path}', typer.colors.RED)
        raise typer.Abort()


def list_path(*, path: Path, exclude_filter: Optional[str] = None, include_filter: Optional[str] = None):
    """

    :param path:
    :param exclude_filter:
    :param include_filter:
    :return:
    """
    folders = os.listdir(path)
    if exclude_filter:
        folders = list(filter(lambda x: exclude_filter not in x, folders))
    if include_filter:
        folders = list(filter(lambda x: include_filter in x, folders))
    return folders


def rename_path(*, src: Path, dst: Path):
    """
    Replace the src name with the dst name.
    :param src:
    :param dst:
    :return:
    """
    os.rename(src, dst)


def delete_file(*, src: Path):
    """
    Delete a specific path
    :param src:
    """
    os.remove(src)
