"""Tests 'autoversion chlog' subcommand."""

from subprocess import PIPE, Popen as popen
from unittest import TestCase
import os
import semver

class TestChangelog(TestCase):
    """Tests 'autoversion chlog' subcommand."""
    LastVersionInitial = '0.0.1'
    LastVersionFull = '3.0.1-alpha+342.peter-dev.202209062328'
    LastVersionRelease = '2.3.7'
        
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    CommitHistoryFile = os.path.join(dir_path, '..', 'res', 'plastic.txt')
    Changelogfile = os.path.join(dir_path, '..', 'CHANGELOG.md')

    def test_new_changelog(self):
        """Tests 'autoversion chlog' subcommand."""
        output = popen(['autoversion', 'chlog',
        '--commit_hist='+self.CommitHistoryFile, "--noupdate"], stdout=PIPE).communicate()[0]
        try:
            changelog = output.decode('utf-8').strip()
            print(changelog)
            self.assertTrue(changelog.startswith("# Changelog"))
            self.assertTrue(changelog.find("All notable changes to this project will be documented in this file. See [conventional commits](https://www.conventionalcommits.org/) for commit guidelines.") > 0)
            self.assertTrue(changelog.find("## v4.1.1 (2022-09-06)") > 0)
            self.assertTrue(changelog.find("## v4.1.0") > 0)
            self.assertTrue(changelog.find("## v4.0.0") > 0)
            self.assertTrue(changelog.find("## v3.0.0") > 0)
            self.assertTrue(changelog.find("## v2.0.0") > 0)
            self.assertTrue(changelog.find("## v1.0.0") > 0)
        except ValueError as e:
            self.fail('autoversion chlog did not return a valid changelog: '+e.__str__())