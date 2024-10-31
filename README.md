# autoversion

A Python tool for [semantic versioning](https://semver.org/) and changelog generation based on source control [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) history.

## Install

* bash (*nix, mingw):
```bash
python -m venv env
source env/bin/activate
pip install -e .[test]
```

* BAT (Windows)
```bat
python -m venv env
env\Scripts\activate
pip install -e .[test]
```

## Test

```
py.test --cov=autoversion --cov-report=term-missing
```

* using provided [plastic.txt](https://github.com/peetonn/autoversion/blob/main/tests/res/plastic.txt)

...bash (*nix, mingw)
```bash
cat tests/plastic.txt | autoversion current --last=1.0.0 -
```

...BAT (Windows)
```bat
type tests\plastic.txt | autoversion current --last=1.0.0 -
```

* using git commits log of this repo:

```
git log --reverse --date="format:%m/%d/%Y %I:%M:%S %p" --pretty="format:%h %ad %s"| autoversion current --last=0.0.1 -
git log --reverse --date="format:%m/%d/%Y %I:%M:%S %p" --pretty="format:%h %ad %s"| autoversion chlog --noupdate -
```

## Usage

* generate current version from commit history given last version:
```
# PlasticSCM
cm find changeset "where branch='/main'" --format="{changesetid} {date} {comment}" --nototal | autoversion current --last=2.2.1 -

# Git
git log --reverse --date="format:%m/%d/%Y %I:%M:%S %p" --pretty="format:%h %ad %s"| autoversion current --last=0.0.1 -
```

* generate changelog based on commit history:

```
# PlasticSCM
cm find changeset "where branch='/main'" --format="{changesetid} {date} {comment}" --nototal | autoversion chlog -

# Git
git log --reverse --date="format:%m/%d/%Y %I:%M:%S %p" --pretty="format:%h %ad %s" | autoversion chlog -
```
