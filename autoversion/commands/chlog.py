"""chlog command."""

import os
import mistletoe
import semver
import re
from json import dumps
from .base import Base
from .base import Commit
from mistletoe import Document
from mistletoe.ast_renderer import ASTRenderer
from datetime import date

class ChangelogGenerator:
    
    OtherChangeTypes = ['perf', 'revert']
    ChangeLogFile = 'CHANGELOG.md'
    Header = """# Changelog

All notable changes to this project will be documented in this file. See [conventional commits](https://www.conventionalcommits.org/) for commit guidelines.

"""

    def __init__(self, changelogMd, changelog, lastVersion):
        self.changelogMdLines = changelogMd.splitlines()
        self.lastVersion = lastVersion
        self.changelog = changelog
        self.commits = []

    def generateChangelog(self, commits):
        if ChangelogGenerator.getChangelogLastVersionIndex(self.changelog) == -1: # add header
            self.addHeader()
            self.insertIndex = len(self.changelogMdLines)
        else:
            self.insertIndex = self.getChangelogInsertIndex()

        self.versionChanges = []
        self.currentVersion = Commit.calculateCurrentVersion(self.lastVersion, commits, self.__onCommitProcessed)
        
        return ChangelogGenerator.render(self.changelogMdLines)

    def __onCommitProcessed(self, version, commit):
        if commit.isVersionCommit():
            self.changelogMdLines[self.insertIndex:self.insertIndex] = ChangelogGenerator.generateVersionEntry(version, commit, self.versionChanges)
            self.versionChanges = []
        else:
            self.versionChanges.append(commit)
    
    def addHeader(self):
        self.changelogMdLines[0:0] = ChangelogGenerator.Header.splitlines()

    def getChangelogInsertIndex(self):
        # iterate over changelog lines and find the first line that starts with lastVersion
        for idx, line in enumerate(self.changelogMdLines):
            if line.startswith('##') and line.find(str(self.lastVersion)) != -1:
                return idx
        return len(ChangelogGenerator.Header.splitlines())
    
    @classmethod
    def render(cls, entryLines):
        return '\n'.join(entryLines)

    @classmethod
    def generateVersionEntry(cls, version, versionCommit, commits):
        versionDate = versionCommit.getDateStr() if versionCommit else date.today().strftime("%Y-%m-%d")
        changelogEntry = '## v{0} ({1})\n\n'.format(version, versionDate)
        if versionCommit is not None and commits is not None:
            commits.append(versionCommit)
            changeTypes = {
                'BREAKING CHANGES': [c for c in commits if c.isBreaking],
                'Features': [c for c in commits if c.type == 'feat' and not c.isBreaking],
                'Bug Fixes': [c for c in commits if c.type == 'fix' and not c.isBreaking],
                'Other': [c for c in commits if c.type in cls.OtherChangeTypes and not c.isBreaking],
            }
            for changeType, changes in changeTypes.items():
                if len(changes) > 0:
                    changelogEntry = changelogEntry + '### {0}\n\n'.format(changeType)
                    for change in changes:
                        changelogEntry += '* {0}\n'.format(change.toChangelogListEntry(changeType == 'Other'))
                    changelogEntry += '\n'
            # changelogEntry += '\n'
        return changelogEntry.splitlines()

    @classmethod
    def fromChangelog(cls, changelogFile = ChangeLogFile, version = None):
        baseVersion = version if version else semver.VersionInfo.parse('0.0.0')
        path = changelogFile if os.path.isabs(changelogFile) else os.path.join(os.getcwd(), changelogFile)
        if os.path.exists(path) and os.path.isfile(path):
            with open(path, 'r') as f:
                # print('>>> reading changelog from {0}'.format(path))
                changelogMd = f.read()
        else:
            # print('>>> changelog file not found at: ' + path + ', creating new changelog file')
            changelogMd = ''
        try:
            changelog = Document(changelogMd)
            latestVersionFromChlog = ChangelogGenerator.getLatestVersion(changelog)
            if latestVersionFromChlog is not None:
                baseVersion = latestVersionFromChlog
                # print('>>> use base version from changelog: ' + str(baseVersion))
            # else:
                # print('>>> base version for changelog: ' + str(baseVersion))
        except Exception as e:
            print('>>> error parsing changelog file: ' + path + ': ' + str(e))
            return None
        return cls(changelogMd, changelog, baseVersion)

    @classmethod
    def getLatestVersion(cls, changelog):
        if changelog.children:
            for child in changelog.children:
                if isinstance(child, mistletoe.block_token.Heading):
                    if child.level == 2:
                        return cls.parseSemVerFromHeading(child)
        return None

    @classmethod
    def parseSemVerFromHeading(cls, heading):
        SemVerRegex = re.compile(r'(?P<version>(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?)')
        headingLine = ''
        if isinstance(heading.children[0], mistletoe.span_token.RawText):
            headingLine = heading.children[0].content
        if isinstance(heading.children[0], mistletoe.span_token.Link):
            headingLine = heading.children[0].children[0].content
        match = SemVerRegex.match(headingLine)
        if match:
            return semver.VersionInfo.parse(match.group('version'))
        return None

    @classmethod
    def getChangelogLastVersionIndex(cls, changelog):
        if changelog.children:
            for i, child in enumerate(changelog.children):
                if isinstance(child, mistletoe.block_token.Heading):
                    if child.level == 2:
                        return i
        return -1

class Chlog(Base):
    ChangeLogFile = 'CHANGELOG.md'

    def __init__(self, options, *args, **kwargs):
        Base.__init__(self, options, args, kwargs)
        self.lastVersion = semver.VersionInfo.parse(self.options['--last']) if self.options['--last'] else None

    def run(self):
        runPath = os.getcwd()
        if self.options['--chlog_file']:
            changeLogPath = self.options['--chlog_file'] if os.path.isabs(self.options['--chlog_file']) else os.path.join(runPath, self.options['--chlog_file'])
        else:
            changeLogPath = os.path.join(runPath, Chlog.ChangeLogFile)
        chlogGenerator = ChangelogGenerator.fromChangelog(changeLogPath, self.lastVersion)
        if chlogGenerator is not None:
            changelog = chlogGenerator.generateChangelog(self.commitHistory)
            if self.options['--noupdate']:
                print(changelog)
            else:
                with open(changeLogPath, 'w') as f:
                    f.write(changelog)
                print(chlogGenerator.currentVersion)
        