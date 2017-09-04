# Changelog
All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Add configuration option for enabling case sensitive proximity matching.
- Ensure that the user submits a unicode encoded file.
- Ensure that all characters are unicode composed characters. This means that
  any decomposed unicode codepoints (é = `b'e\xcc\x81'`) are converted into
  composed codepoints (é = `b'\xc3\xa9'`). Otherwise `'μῆνιν' == 'μῆνιν'` might
  return false and fail to match where there are matches.
- Ignore `\sidenote` in sameword matching. This means for example that if a
  `\sidenote` intervenes between two words that would constitute a match, it is
  appropriately ignored and they match.
- Ignore content after line comments on same word comparison.
- Add customization option for whether to compare same words in lower case
  forms.
- Add `--config-file` command line argument that makes it possible to use
  general configuration file. The configuration file currently supports
  including and excluding macros for same word matching and defining ellipsis
  patterns.
- CHANGELOG.md!

### Removed
- `--include-macros` and `--exclude-macros` are no longer supported as command
  line arguments. The configuration file setup should be used in stead. The
  arguments are used as keys in JSON file (`include_macros` and
  `exclude_macros`) where the value is a list of patterns that should be
  included or excluded. See the documentation on the configuration file.

### Changed
- Code refactoring and improvement of some tests.
- Make word matching case-insensitive.
- Sameword matching improved. Handling and cleaning of main text words for
  string comparison has been significantly improved to represent all and only
  words that occur in the main text. This includes facilities for defining which
  `LaTeX` macros should be included in or excluded from sameword comparisons.
- Better preserve and handle whitespace such as linebreaks and tabs when
  processing `\edtext{}` notes.
- Preserve whitespace in the text, but don't include it in sameword comparisons.
- Remove the dependency on `docopt`, creating a package without any external
  dependencies.
- Read the documents in binary rather than text mode.

