#!/usr/bin/python3
"""Apply a shell command in parallel by using a multiprocessing.pool."""
import configparser
import subprocess
import sys
import time
from copy import copy
from multiprocessing import Pool, cpu_count
from pathlib import Path

_REQUIRED_NUMBER_OR_ARGS = 3

def _get_configuration() -> dict:
    """Get configuration parameters from papply.ini.

    This file can be locate either in the current directory or the user home
    """
    config = configparser.ConfigParser()
    if config.read([Path("./papply.ini"), Path("~/papply.ini").expanduser()]):
        default = config["papply"]
        num_cores = default.getint("num_cores", cpu_count())
        overcommit_factor = default.getint("overcommit_factor", 1)
        show_progress = default.get("show_progress", "iflong")
        long_duration = default.getint("long_duration", 60)
    else:
        num_cores = cpu_count()
        overcommit_factor = 1
        show_progress = "iflong"
        long_duration = 60

    # want to disable progress indication?
    bool_show_progress = show_progress.lower() not in ["n", "no", "0", "false"]

    # want to always enable progress indication?
    if show_progress.lower() in ["y", "yes", "1", "true"]:
        long_duration = 0

    return {
        "num_threads": num_cores * overcommit_factor,
        "show_progress": bool_show_progress,
        "long_duration": long_duration,
    }


def _replace_variables(command: str, argument: str) -> str:
    """Replace template placeholders (directory, name, extension, ...) from the argument."""
    if "%" not in command:
        return command
    command_expanded = copy(command)
    argument_path = Path(argument)
    dirname = str(argument_path.parents[0]) if argument_path.parents else ""
    extension = argument_path.suffixes[-1] if argument_path.suffixes else ""

    for template, value in [
            ("%F", argument),
            ("%d", dirname),
            ("%f", str(argument_path.name)),
            ("%n", str(argument_path.stem)),
            ("%e", extension),
            ("%z", ""),
    ]:
        command_expanded = command_expanded.replace(template, value)
    return command_expanded


def _apply_one(argument: str) -> None:
    """Apply the command to one argument."""
    # the original command passed on the command line
    command = sys.argv[1]
    command_expanded = _replace_variables(command, argument)

    # if the command is not expanded add the argument to the basic command
    # otherwise assume that the command_expanded is complete
    if command_expanded == command:
        command_expanded = f'{command} "{argument}"'

    try:
        reply = subprocess.check_output(
            command_expanded,
            universal_newlines=True,
            shell=True,
            stderr=subprocess.DEVNULL,
        )
        # if there was output to stdout print it here
        if reply:
            print(reply.rstrip("\r\n"))
    except subprocess.CalledProcessError:
        # something went wrong inform the user
        print(f'"{command_expanded}" did not succeed')


def main() -> None:
    """Execute the main logic of papply. It creates the multiprocessing pool."""
    if len(sys.argv) < _REQUIRED_NUMBER_OR_ARGS:
        print('Usage: papply "some command with arguments" files')
        print('Example: papply "gzip -9" *.ps')
        print()
        print("The following variables can used in the command:")
        print(" %F: Full original input")
        print(" %d: directory name (no trailing slash)")
        print(" %f: file name with extension")
        print(" %n: file name without extension")
        print(" %e: extension (with leading .)")
        print(" %z: empty string")
        print()
        print('Example: papply "convert -set colorspace Gray %F %n_gray.jpg" *.ps')
        sys.exit()

    # sys.argv[1] is the command line to call in parallel
    # anything after sys.argv[1] are arguments to this command line
    arguments = sys.argv[2:]
    narguments = len(arguments)

    config_values = _get_configuration()

    # register when we consider the execution to take long
    if config_values["show_progress"]:
        if config_values["long_duration"] == 0:
            long_running = True
        else:
            long_running = False
            long_limit = time.monotonic() + config_values["long_duration"]
        # iteration number that corresponds to
        # 10, 20, .., 90 step in progress
        progress_marks = [round(x/100.0*narguments) for x in range(10, 100, 10)]

    pool = Pool(config_values["num_threads"])
    for i, _ in enumerate(pool.imap(_apply_one, arguments)):
        # when this starts to be a long running process print percentage
        # (10%) progress
        if config_values["show_progress"] and long_running and (i+1) in progress_marks:
            print(f"PAPPLY: {i+1} of {narguments} commands executed")

        if config_values["show_progress"] and not long_running:
            # check to see if it is long running
            long_running = time.monotonic() > long_limit

    pool.close()
    pool.join()


if __name__ == "__main__":
    main()
