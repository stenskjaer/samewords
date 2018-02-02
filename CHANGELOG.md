# Changelog
All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [0.2.6]
### Changed
- Updated `setyp.py` with `data_files` to actually include what has already been
  included in the MANIFEST in bdist build too(!)

## [0.2.5]
### Changed
- Updated the MANIFEST to actually include the assets.

## [0.2.4]
### Added
- The amount of words compared in the context is now configurable.
- MANIFEST.in file for including test assets.

### Changed
- The default context comparison distance is reduced from 30 to 20.

## [0.2.3]
### Added
- Proper handling of escaped LaTeX characters.

### Removed
- Dependecy on Docopt.

### Changed
- Use reStructuredText for the README.

## [0.2.0]
### Added
- Context length matching *exactly* 30 content words rather than *at least*.
- Completely rewritten underlying system with significantly simplified
  tokenization and matching approach. 
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
- Handle LaTeX comments correctly, which means ignore them and match across
  comments.
- Add customization option for whether to compare same words in lower case
  forms.
- Add `--config-file` command line argument that makes it possible to use
  general configuration file. The configuration file currently supports
  including and excluding macros for same word matching and defining ellipsis
  patterns.
- CHANGELOG.md!

### Fixed
- Sameword matches in `\lemma{}`-macros were incorrectly annotated


### Removed
- `include_macros` is no longer a config file option as it corresponds to not
  adding a macro to the `exclude_macros` list. Almost all macros are included by
  default.
- `--include-macros` and `--exclude-macros` are no longer supported as command
  line arguments. The configuration file setup should be used in stead. The
  arguments are used as keys in JSON file (`include_macros` and
  `exclude_macros`) where the value is a list of patterns that should be
  included or excluded. See the documentation on the configuration file.

### Changed
- Ignored macros are not included in the sameword wrap when they follow a match. 
- Code refactoring and improvement of some tests.
- Include `\index{}` in `exclude_macros` by default. Index macros should always
  be ignored as their content is not relevant to the content of the text (it's
  never printed), so although they may contain different content, the word that
  they may precede should still be disambiguated.
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

