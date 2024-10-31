"""Tests 'autoversion release' subcommand."""

from subprocess import PIPE, Popen as popen
from unittest import TestCase
import os
import semver

class TestRelease(TestCase):
    """Tests 'autoversion release' subcommand."""
    LastVersionInitial = '0.0.1'
    LastVersionFull = '3.0.1-alpha+342.peter-dev.202209062328'
    LastVersionRelease = '2.3.7'
        
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    CommitHistoryFile = os.path.join(dir_path, '..', 'res', 'plastic.txt')
    Changelogfile = os.path.join(dir_path, '..', 'CHANGELOG.md')

    def test_new_release(self):
        """Tests 'autoversion release' subcommand."""
        output = popen(['autoversion', 'release',
        '--current='+self.LastVersionRelease,
        '--commit_hist='+self.CommitHistoryFile], stdout=PIPE).communicate()[0]
        try:
            changelog = output.decode('utf-8').strip()
            # print(changelog)
            self.assertTrue(changelog.find(self.LastVersionRelease) > 0)
        except ValueError as e:
            self.fail('autoversion release did not return a valid release note: '+e.__str__())

    def test_new_release_with_empty_commits_history(self):
        """Tests 'autoversion release' subcommand."""
        emptyFile = os.path.join(self.dir_path, '..', 'res', 'empty.txt')
        with open(emptyFile, "w+") as f:
            output = popen(['autoversion', 'release',
            '--current='+self.LastVersionRelease,
            '--commit_hist='+emptyFile], stdout=PIPE).communicate()[0]
            try:
                changelog = output.decode('utf-8').strip()
                print(changelog)
                self.assertTrue(changelog.find(self.LastVersionRelease) > 0)
                self.assertTrue(len(changelog.splitlines()) == 1)
            except ValueError as e:
                self.fail('autoversion release did not return a valid release note: '+e.__str__())
        os.remove(emptyFile)