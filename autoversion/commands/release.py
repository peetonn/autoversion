"""release command"""

import semver
from .base import Base
from .chlog import ChangelogGenerator

class Release(Base):

    def __init__(self, options, *args, **kwargs):
        Base.__init__(self, options, args, kwargs)
        self.lastVersion = semver.VersionInfo.parse(self.options['--current']) if self.options['--current'] else None

    def run(self):
        if len(self.commitHistory):
            lines = ChangelogGenerator.generateVersionEntry(self.lastVersion, self.commitHistory[-1], self.commitHistory[0:-1])
        else:
            lines = ChangelogGenerator.generateVersionEntry(self.lastVersion, None, None)
        print('\n'.join(lines))