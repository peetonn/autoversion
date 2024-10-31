"""Tests for changelog generation"""

import os
import unittest
import semver
from autoversion.commands.chlog import ChangelogGenerator
from autoversion.commands.base import Commit
from test_parse import TestParseCommit

class TestChangelogGenerator(unittest.TestCase):
    """Tests for changelog generation"""
    LastVersionInitial = '0.0.1'
    LastVersionFull = '3.0.1-alpha+342.peter-dev.202209062328'
    LastVersionRelease = '2.3.7'
        
    dir_path = os.path.dirname(os.path.realpath(__file__))
    ChangelogFile = os.path.join(dir_path, 'res', 'CHANGELOG.md')

    def test_generate_version_entry_with_features(self):
        """Tests generating changelog version entry."""
        
        commits = [Commit.parseCommit(TestParseCommit.commit6), 
            Commit.parseCommit(TestParseCommit.commit5)]

        versionEntry = ChangelogGenerator.generateVersionEntry(semver.VersionInfo.parse(TestChangelogGenerator.LastVersionInitial), commits[0], commits[1:])
        self.assertIsNotNone(versionEntry)
        self.assertEqual(len(versionEntry), 6)
        
        rendered = ChangelogGenerator.render(versionEntry)
        self.assertIsNotNone(rendered)
        
        self.assertTrue(rendered.startswith("## v0.0.1 ()"))
        self.assertTrue(rendered.find("### Bug Fixes") == -1)
        self.assertTrue(rendered.find("### Features") > 0)
        self.assertTrue(rendered.find("### BREAKING CHANGES") == -1)
        self.assertTrue(rendered.find("### Other") == -1)
        self.assertTrue(rendered.find(commits[0].summary) > 0) # expect commit6 to be in the changelog
        self.assertFalse(rendered.find(commits[1].summary) > 0) # don't expect commit5 to be in the changelog

    def test_generate_version_entry_with_breaking_changes(self):
        """Tests generating changelog version entry with breaking changes and other fixes."""
        
        commits = [Commit.parseCommit(TestParseCommit.commit4), 
            Commit.parseCommit(TestParseCommit.commit3), 
            Commit.parseCommit(TestParseCommit.commit1),
            Commit.parseCommit(TestParseCommit.commit7),
            Commit.parseCommit('perf: optimize HTTP requests scheduling\n')]

        versionEntry = ChangelogGenerator.generateVersionEntry(semver.VersionInfo.parse(TestChangelogGenerator.LastVersionRelease), commits[0], commits[1:])
        self.assertIsNotNone(versionEntry)
        
        rendered = ChangelogGenerator.render(versionEntry)
        self.assertIsNotNone(rendered)
        print(rendered)
        
        self.assertTrue(rendered.startswith("## v2.3.7 ()"))
        self.assertTrue(rendered.find("### Bug Fixes") > 0)
        self.assertFalse(rendered.find("### Features") > 0)
        self.assertTrue(rendered.find("### BREAKING CHANGES") > 0)
        self.assertTrue(rendered.find("### Other") > 0)

    def test_changelog_init_from_file(self):
        """Tests initialize changelog generator from file."""
        generator = ChangelogGenerator.fromChangelog(self.ChangelogFile)
        self.assertIsNotNone(generator)
        self.assertEqual(str(generator.lastVersion), "3.1.25")

    def test_generate_new_changelog_from_commits(self):
        """Tests generating a new changelog from commits."""

        commits = []
        for idx in range(1,8):
            commits.append(Commit.parseCommit(getattr(TestParseCommit, 'commit' + str(idx))))

        chlogGen = ChangelogGenerator.fromChangelog('non-existent-file')
        self.assertIsNotNone(chlogGen)
        self.assertEqual(str(chlogGen.lastVersion), "0.0.0")

        changelog = chlogGen.generateChangelog(commits)
        print(changelog)

        self.assertIsNotNone(changelog)
        self.assertEqual(chlogGen.currentVersion, semver.VersionInfo.parse('4.1.1'))
        self.assertTrue(changelog.startswith("# Changelog"))
        self.assertTrue(changelog.find("All notable changes to this project will be documented in this file. See [conventional commits](https://www.conventionalcommits.org/) for commit guidelines.") > 0)
        self.assertTrue(changelog.find("## v4.1.1") > 0)
        self.assertTrue(changelog.find("## v4.1.0") > 0)
        self.assertTrue(changelog.find("## v4.0.0") > 0)
        self.assertTrue(changelog.find("## v3.0.0") > 0)
        self.assertTrue(changelog.find("## v2.0.0") > 0)
        self.assertTrue(changelog.find("## v1.0.0") > 0)
        self.assertEqual(changelog.count("### Features"), 1)
        self.assertEqual(changelog.count("### Bug Fixes"), 1)
        self.assertEqual(changelog.count("### BREAKING CHANGES"), 4)

    def test_generate_new_changelog_from_empty_history(self):
        """Tests generating a new changelog from empty commits history."""

        chlogGen = ChangelogGenerator.fromChangelog('non-existent-file')
        self.assertIsNotNone(chlogGen)
        self.assertEqual(str(chlogGen.lastVersion), "0.0.0")

        changelog = chlogGen.generateChangelog([])
        # print(changelog)

        self.assertIsNotNone(changelog)
        self.assertEqual(chlogGen.currentVersion, semver.VersionInfo.parse('0.0.0'))
        self.assertTrue(changelog.startswith("# Changelog"))
        self.assertTrue(changelog.find("All notable changes to this project will be documented in this file. See [conventional commits](https://www.conventionalcommits.org/) for commit guidelines.") > 0)
        self.assertEqual(len(changelog.splitlines()), 3)

    def test_update_changelog_from_commits(self):
        """Tests update existing changelog from commit history."""
        generator = ChangelogGenerator.fromChangelog(self.ChangelogFile)
        self.assertIsNotNone(generator)
        self.assertEqual(str(generator.lastVersion), "3.1.25")
        
        commits = []
        for idx in range(1,8):
            commits.append(Commit.parseCommit(getattr(TestParseCommit, 'commit' + str(idx))))
        changelog = generator.generateChangelog(commits)
        # print(changelog)

        self.assertIsNotNone(changelog)
        self.assertEqual(generator.currentVersion, semver.VersionInfo.parse('7.1.1'))
        self.assertTrue(changelog.startswith("# Changelog"))
        self.assertTrue(changelog.find("All notable changes to this project will be documented in this file. See [conventional commits](https://www.conventionalcommits.org/) for commit guidelines.") > 0)
        