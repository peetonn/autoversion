"""Tests for commit history parsing."""

from unittest import TestCase
from autoversion.commands import *
import os 

class TestParseCommit(TestCase):
    """Tests conventional commit messages parsing."""

    # test commits taken from here -- https://www.conventionalcommits.org/en/v1.0.0/#examples
    commit1 = """feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
"""
    commit2 = """feat!: send an email to the customer when a product is shipped
"""
    commit3 = """feat(api)!: send an email to the customer when a product is shipped
"""
    commit4 = """chore!: drop support for Node 6

BREAKING CHANGE: use JavaScript features not available in Node 6.

"""
    commit5 = """docs: correct spelling of CHANGELOG
"""
    commit6 = """feat(lang): add Polish language
"""
    commit7 = """fix: prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Remove timeouts which were used to mitigate the racing issue but are
obsolete now.

Reviewed-by: Z
Refs: #123
"""
    def test_parse_commit_message1(self):
        parsed = Commit.parseCommit(self.commit1)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.hash, '')
        self.assertEqual(parsed.type, 'feat')
        self.assertIsNone(parsed.scope)
        self.assertEqual(parsed.summary, 'allow provided config object to extend other configs')
        self.assertEqual(parsed.body, '')
        self.assertEqual(parsed.footer, 'BREAKING CHANGE: `extends` key in config file is now used for extending other config files')
        self.assertEqual(parsed.footerToken, 'BREAKING CHANGE')
        self.assertEqual(parsed.footerValue, '`extends` key in config file is now used for extending other config files')
        self.assertEqual(parsed.isBreaking, True)
        self.assertEqual(parsed.isMerge, False)
        self.assertEqual(parsed.isInitial, False)

    def test_parse_commit_message2(self):
        parsed = Commit.parseCommit(self.commit2)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.hash, '')
        self.assertEqual(parsed.type, 'feat')
        self.assertIsNone(parsed.scope)
        self.assertEqual(parsed.summary, 'send an email to the customer when a product is shipped')
        self.assertEqual(parsed.body, '')
        self.assertEqual(parsed.footer, '')
        self.assertIsNone(parsed.footerToken)
        self.assertIsNone(parsed.footerValue)
        self.assertEqual(parsed.isBreaking, True)
        self.assertEqual(parsed.isMerge, False)
        self.assertEqual(parsed.isInitial, False)

    def test_parse_commit_message3(self):
        parsed = Commit.parseCommit(self.commit3)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.hash, '')
        self.assertEqual(parsed.type, 'feat')
        self.assertEqual(parsed.scope, 'api')
        self.assertEqual(parsed.summary, 'send an email to the customer when a product is shipped')
        self.assertEqual(parsed.body, '')
        self.assertEqual(parsed.footer, '')
        self.assertIsNone(parsed.footerToken)
        self.assertIsNone(parsed.footerValue)
        self.assertEqual(parsed.isBreaking, True)
        self.assertEqual(parsed.isMerge, False)
        self.assertEqual(parsed.isInitial, False)

    def test_parse_commit_message4(self):
        print(self.commit4)
        parsed = Commit.parseCommit(self.commit4)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.hash, '')
        self.assertEqual(parsed.type, 'chore')
        self.assertIsNone(parsed.scope)
        self.assertEqual(parsed.summary, 'drop support for Node 6')
        self.assertEqual(parsed.body, '')
        self.assertEqual(parsed.footer, 'BREAKING CHANGE: use JavaScript features not available in Node 6.')
        self.assertEqual(parsed.footerToken, 'BREAKING CHANGE')
        self.assertEqual(parsed.footerValue, 'use JavaScript features not available in Node 6.')
        self.assertEqual(parsed.isBreaking, True)
        self.assertEqual(parsed.isMerge, False)
        self.assertEqual(parsed.isInitial, False)

    def test_parse_commit_message5(self):
        parsed = Commit.parseCommit(self.commit5)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.hash, '')
        self.assertEqual(parsed.type, 'docs')
        self.assertIsNone(parsed.scope)
        self.assertEqual(parsed.summary, 'correct spelling of CHANGELOG')
        self.assertEqual(parsed.body, '')
        self.assertEqual(parsed.footer, '')
        self.assertIsNone(parsed.footerToken)
        self.assertIsNone(parsed.footerValue)
        self.assertEqual(parsed.isBreaking, False)
        self.assertEqual(parsed.isMerge, False)
        self.assertEqual(parsed.isInitial, False)

    def test_parse_commit_message6(self):
        parsed = Commit.parseCommit(self.commit6)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.hash, '')
        self.assertEqual(parsed.type, 'feat')
        self.assertEqual(parsed.scope, 'lang')
        self.assertEqual(parsed.summary, 'add Polish language')
        self.assertEqual(parsed.body, '')
        self.assertEqual(parsed.footer, '')
        self.assertIsNone(parsed.footerToken)
        self.assertIsNone(parsed.footerValue)
        self.assertEqual(parsed.isBreaking, False)
        self.assertEqual(parsed.isMerge, False)
        self.assertEqual(parsed.isInitial, False)

    def test_parse_commit_message7(self):
        parsed = Commit.parseCommit(self.commit7)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.hash, '')
        self.assertEqual(parsed.type, 'fix')
        self.assertIsNone(parsed.scope)
        self.assertEqual(parsed.summary, 'prevent racing of requests')
        print(parsed.body)
        self.assertEqual(parsed.body, """Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Remove timeouts which were used to mitigate the racing issue but are
obsolete now.""")
        self.assertEqual(parsed.footer, """Reviewed-by: Z
Refs: #123""")
        self.assertEqual(parsed.footerToken, 'Refs')
        self.assertEqual(parsed.footerValue, '#123')
        self.assertEqual(parsed.isBreaking, False)
        self.assertEqual(parsed.isMerge, False)
        self.assertEqual(parsed.isInitial, False)

    def test_parse_commit_without_newline(self):
        commitMsg = 'feat: add get plugin version function'
        parsed = Commit.parseCommit(commitMsg)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.hash, '')
        self.assertEqual(parsed.type, 'feat')
        self.assertEqual(parsed.typeEnum, CommitType.Feature)
        self.assertIsNone(parsed.scope)
        self.assertEqual(parsed.summary, 'add get plugin version function')
        self.assertEqual(parsed.body, '')
        self.assertEqual(parsed.footer, '')
        self.assertIsNone(parsed.footerToken)
        self.assertIsNone(parsed.footerValue)
        self.assertEqual(parsed.isBreaking, False)
        self.assertEqual(parsed.isMerge, False)
        self.assertEqual(parsed.isInitial, False)

class TestParseCommitHistory(TestCase):
    """Tests conventional commit log parsing."""
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    LogFile = os.path.join(dir_path, 'res', 'plastic.txt')

    def test_parse_commit_history(self):
        with open(self.LogFile, 'r') as f:
            commits = Commit.parseCommitHistory(f)
            self.assertIsNotNone(commits)
            self.assertEqual(len(commits), 10)
            
            self.assertEqual(commits[0].hash, '2')
            self.assertEqual(commits[0].type, 'feat')
            self.assertEqual(commits[0].body, '')
            self.assertEqual(commits[0].footer, '')

            self.assertEqual(commits[1].hash, '5')
            self.assertEqual(commits[1].type, 'feat')
            self.assertEqual(commits[2].hash, '7')
            self.assertEqual(commits[2].type, 'fix')
            self.assertEqual(commits[3].hash, '8')
            self.assertEqual(commits[3].type, 'feat')
            self.assertEqual(commits[3].isBreaking, True)
            self.assertEqual(commits[4].hash, '9')
            self.assertEqual(commits[4].type, 'feat')
            self.assertEqual(commits[4].isBreaking, True)
            self.assertEqual(commits[5].hash, '10')
            self.assertEqual(commits[5].type, 'feat')
            self.assertEqual(commits[5].isBreaking, True)
            self.assertEqual(commits[6].hash, '11')
            self.assertEqual(commits[6].type, 'chore')
            self.assertEqual(commits[6].isBreaking, True)
            self.assertEqual(commits[7].hash, '12')
            self.assertEqual(commits[7].type, 'docs')
            self.assertEqual(commits[7].isBreaking, False)
            self.assertEqual(commits[8].hash, '13')
            self.assertEqual(commits[8].type, 'feat')
            self.assertEqual(commits[8].isBreaking, False)
            self.assertEqual(commits[9].hash, '14')
            self.assertEqual(commits[9].type, 'fix')
            self.assertEqual(commits[9].isBreaking, False)
            self.assertEqual(commits[9].summary, 'prevent racing of requests')
            self.assertEqual(commits[9].body,  """Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Remove timeouts which were used to mitigate the racing issue but are
obsolete now.""")
            self.assertEqual(commits[9].footer,  """Reviewed-by: Z
Refs: #123""")
            self.assertEqual(commits[9].footerToken, 'Refs')
            self.assertEqual(commits[9].footerValue, '#123')