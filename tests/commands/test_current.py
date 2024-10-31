"""Tests 'autoversion current' subcommand."""

from subprocess import PIPE, Popen as popen
from unittest import TestCase
import os
import semver

class TestCurrent(TestCase):
    """Tests 'autoversion current' subcommand."""
    LastVersionInitial = '0.0.1'
    LastVersionFull = '3.0.1-alpha+342.peter-dev.202209062328'
    LastVersionRelease = '2.3.7'
    LastVersionPrefxed = 'v0.0.1'
        
    dir_path = os.path.dirname(os.path.realpath(__file__))
    LogFile = os.path.join(dir_path, '..', 'res', 'plastic.txt')

    def test_current(self):
        """Tests 'autoversion current' subcommand."""
        output = popen(['autoversion', 'current', 
        '--last='+self.LastVersionInitial, 
        '--commit_hist='+self.LogFile], stdout=PIPE).communicate()[0]
        try:
            current = semver.VersionInfo.parse(output.decode('utf-8').strip())
            self.assertIsNotNone(current)
            self.assertEqual(current.major, 4)
            self.assertEqual(current.minor, 1)
            self.assertEqual(current.patch, 1)
        except ValueError as e:
            self.fail('autoversion current did not return a valid semver version: '+e.__str__())

    def test_current_version_prefixed(self):
        output = popen(['autoversion', 'current', 
        '--last='+self.LastVersionPrefxed, 
        '--commit_hist='+self.LogFile], stdout=PIPE).communicate()[0]
        try:
            current = semver.VersionInfo.parse(output.decode('utf-8').strip())
            self.assertIsNotNone(current)
            self.assertEqual(current.major, 4)
            self.assertEqual(current.minor, 1)
            self.assertEqual(current.patch, 1)
        except ValueError as e:
            self.fail('autoversion current did not return a valid semver version: '+e.__str__())

    def test_invalid_last_version(self):
        output = popen(['autoversion', 'current', 
        '--last=invalid-version', 
        '--commit_hist='+self.LogFile], stdout=PIPE).communicate()[0]
        try:
            current = semver.VersionInfo.parse(output.decode('utf-8').strip())
            self.fail('autoversion current did not return an error for an invalid last version')            
        except ValueError as e:
            self.assertIsNotNone(e)


