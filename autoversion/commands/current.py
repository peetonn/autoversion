"""chlog command."""

from .base import Base
from .base import Commit
from json import dumps
import semver

class Current(Base):
    def __init__(self, options, *args, **kwargs):
        Base.__init__(self, options, args, kwargs)
        self.lastVersion = semver.VersionInfo.parse(self.options['--last']) if self.options['--last'] else semver.VersionInfo.parse('0.0.0')

    def run(self):
        currentVersion = Commit.calculateCurrentVersion(self.lastVersion, self.commitHistory)
        print(str(currentVersion))
