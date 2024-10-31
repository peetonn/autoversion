"""
autoversion

Usage:
    autoversion current --last=<last_version> (--commit_hist=<commit_history_file> | -)
    autoversion chlog [--last=<last_version>] [--chlog_file=<changelog_file>] [--noupdate] (--commit_hist=<commit_history_file> | -)
    autoversion release --current=<current_version> (--commit_hist=<commit_history_file> | -)
    autoversion --version

Arguments:
    current     Calculate current version based on commit history and last version
    chlog       Generate changelog for the current version (if CHANGELOG.md exists) and all versions (otherwise)

Options:
    --last=<last_version>                The last version
    --current=<current_version>          The current version
    --commit_hist=<commit_history_file>  The commit history file
    --chlog_file=<changelog_file>        The existing changelog file
    --noupdate                           Don't update the changelog file (print to stdout)
    -                                    Read from stdin
    --version                            Show version

Examples:
    autoversion current --last=0.0.1 --commit_hist=commit_history.txt
    autoversion chlog --commit_hist=commit_history.txt
    autoversion chlog --chlog_file=docs/CHANGELOG.md --commit_hist=commit_history.txt
    git log --reverse --pretty="format:%h %s" | autoversion current --last=0.0.1 -
    git log --reverse --date="format:%m/%d/%Y %I:%M:%S %p" --pretty="format:%h %ad %s"| autoversion current --last=0.0.1 -
    cm find changeset "where branch='/main'" --format="{changesetid} {date} {comment}" --nototal | autoversion current --last=2.2.1 -
    cm find changeset "where branch='/main'" --format="{changesetid} {date} {comment}" --nototal | autoversion chlog -
""" 

from docopt import docopt
import semver
import sys

from inspect import getmembers, isclass
from . import __version__ as VERSION

def main():
    """Main CLI entrypoint."""
    import autoversion.commands
    options = docopt(__doc__, version=VERSION)

    for (k, v) in options.items():
        if hasattr(autoversion.commands, k) and v:
            module = getattr(autoversion.commands, k)
            commands = getmembers(module, isclass)
            command = [(name,cls) for (name,cls) in commands if name.lower() == k][0][1]
            autoversion.commands = commands
            command = command(options)
            command.run()
