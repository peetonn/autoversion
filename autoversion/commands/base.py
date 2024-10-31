"""The base command."""

import sys
import semver
import re
import datetime
from json import dumps
from enum import Enum

# adapted from https://github.com/jgoodman8/pyhist#commits-specification
class CommitType(Enum):
    Build = "build"
    Chore = "chore"
    Ci = "ci"
    Docs = "docs"
    Feature = "feat"
    Fix = "fix"
    Performance = "perf"
    Refactor = "refactor"
    Release = "release"
    Revert = "revert"
    Style = "style"
    Test = "test"

    @classmethod
    def fromToken(cls, token):
        tokenDict = {
            "build": CommitType.Build,
            "chore": CommitType.Chore,
            "ci": CommitType.Ci,
            "docs": CommitType.Docs,
            "feat": CommitType.Feature,
            "fix": CommitType.Fix,
            "perf": CommitType.Performance,
            "refactor": CommitType.Refactor,
            "release": CommitType.Release,
            "revert": CommitType.Revert,
            "style": CommitType.Style,
            "test": CommitType.Test
        }
        if token in tokenDict:
            return tokenDict[token]
        return None

class Commit:
    CommitRegex = re.compile(r"(?P<initial_commit>^Initial commit\.?)|(?P<merge>^Merge [^\r\n]+)|(?P<type>^build|chore|ci|docs|feat|fix|perf|refactor|release|revert|style|test|¯\\_\(ツ\)_\/¯)(?:\((?P<scope>[\w-]+)\))?(?P<breaking>!)?: (?P<summary>[\w ,'.`:-]+)(\n)*(?P<body>[\w\s ,'.`\[\]-]+)(?P<footer>(?<=\n)(?:(?P<footer_token>[\w\s-]+): (?P<footer_value>[\w -`]+))+|$)", re.MULTILINE)
    HistoryLineRegex = re.compile(r'^(?P<hash>[a-fA-F0-9]+) (?P<date>\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2} (A|P)M) (?P<description>(?:.|\n)+)$', re.MULTILINE)

    def __init__(self, commitHash, commitType, commitScope, commitSummary, commitBody, commitFooter, isInitial = False,
        isMerge=False, isBreaking=False, footerToken=None, footerValue=None):
        self.hash = commitHash
        self.type = commitType
        self.typeEnum = CommitType.fromToken(commitType)
        self.scope = commitScope
        self.summary = commitSummary.rstrip() if commitSummary else ''
        self.body = commitBody.rstrip() if commitBody else ''
        self.footer = commitFooter.rstrip() if commitFooter else ''
        self.isMerge = isMerge
        self.isInitial = isInitial
        self.isBreaking = isBreaking
        self.footerToken = footerToken.strip() if footerToken else None
        self.footerValue = footerValue.strip() if footerValue else None
        self.date = None

    def __str__(self):
        return f"{self.hash} {self.type} {self.scope} {self.summary} {self.body} {self.footer}"

    def isVersionCommit(self):
        return self.typeEnum in [CommitType.Feature, CommitType.Fix] or self.isBreaking

    def toChangelogListEntry(self, skipBody):
        entry = '{0}'.format(self.summary) if skipBody or len(self.body) == 0 else '{0}\n\n{1}\n'.format(self.summary, self.body)
        if self.scope:
            entry = '**{0}:** {1}'.format(self.scope, entry)
        if self.isBreaking and self.footerValue:
            entry = '{0}\n\n{1}'.format(entry, self.footerValue)
        return entry

    def getDateStr(self):
        return self.date.strftime('%Y-%m-%d') if self.date else ''

    @classmethod
    def parseCommit(cls, commitString):
        if not commitString.endswith('\n'):
            commitString += '\n'
        commitMatch = cls.CommitRegex.match(commitString)
        if commitMatch:
            isInitial = commitMatch.group('initial_commit') is not None
            isMerge = commitMatch.group('merge') is not None
            isBreaking = commitMatch.group('breaking') is not None or commitMatch.group('footer_token') == 'BREAKING CHANGE'
            commitType = commitMatch.group('type')
            commitScope = commitMatch.group('scope')
            commitSummary = commitMatch.group('summary')
            commitBody = commitMatch.group('body')
            commitFooter = commitMatch.group('footer')
            commitFooterToken = commitMatch.group('footer_token')
            commitFooterValue = commitMatch.group('footer_value')
            return Commit('', commitType, commitScope, commitSummary, commitBody, commitFooter, isInitial, isMerge, isBreaking, commitFooterToken, commitFooterValue)
        return None

    @classmethod
    def parseCommitHistory(cls, stream):
        commitHist = []
        lastCommitId = ''
        lastCommitLine = ''
        for line in iter(stream.readline, ''):
            match = cls.HistoryLineRegex.match(line)
            if match:
                if len(lastCommitLine):
                    # print('>>> parse commit: ' + repr(lastCommitLine))
                    commit = Commit.parseCommit(lastCommitLine)
                    if commit is not None:
                        commit.hash = lastCommitId
                        commit.date = lastCommitDate
                        commitHist.append(commit)
                    else:
                        # print('>>> discard commit line: ' + lastCommitLine)
                        pass
                    lastCommitLine = ''
                lastCommitId = match.group('hash')
                lastCommitDate = datetime.datetime.strptime(match.group('date'), '%m/%d/%Y %I:%M:%S %p')
                lastCommitLine = match.group('description')
                # print('>>> commit decrption: ' + repr(lastCommitLine))
            else:
                lastCommitLine += line
        # finalize last commit
        if len(lastCommitLine):
            commit = Commit.parseCommit(lastCommitLine)
            if commit is not None:
                commit.hash = lastCommitId
                commit.date = lastCommitDate
                commitHist.append(commit)
            else:
                # print('>>> discard commit line: ' + lastCommitLine)
                pass
        return commitHist

    @classmethod
    def calculateCurrentVersion(cls, lastVersion, commitHistory, commitProcessedCb = None):
        currentVersion = lastVersion
        for commit in commitHistory:
            if commit.isBreaking:
                currentVersion = currentVersion.bump_major()
            elif commit.type == 'feat':
                currentVersion = currentVersion.bump_minor()
            elif commit.type == 'fix':
                currentVersion = currentVersion.bump_patch()
            if commitProcessedCb:
                commitProcessedCb(currentVersion, commit)
        currentVersion = currentVersion.finalize_version()
        return currentVersion

class Base(object):
    """A base command."""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs
        self.lastVersion = None
        self.parseOptions()

    def run(self):
        raise NotImplementedError('You must implement the run() method yourself!')

    def parseOptions(self):
        if self.options['--last'] and self.options['--last'].startswith('v'):
            self.options['--last'] = self.options['--last'][1:]
        if self.options['-']:
            self.commitHistory =  Commit.parseCommitHistory(sys.stdin)
        else:
            self.commitHistory = Commit.parseCommitHistory(open(self.options['--commit_hist'], 'r', encoding='utf-8'))
