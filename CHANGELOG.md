# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)

## [0.6.0]
### Added
- Added CLI commands for `assistants list` and `assistants clean`
- Automatic cleanup of any extra assistants in user account when initiating chat
- Added docstrings for undocumented functions
- Test case coverage for most OpenAI chat and vector store operations [#15](https://github.com/jbencina/vecsync/issues/15)

### Changed
- Updated CLI chat command to `vs chat`
- Refactored CLI into separate modules
- Removed assistant ID persistance from settings file and only attempt to retrieve assistant from API

## [0.5.1]
### Fixed
- Fixed bug where an incorrect thread ID was referenced causing chats to fail
- Add support for Python >= 3.10

## [0.5.0]
### Added
- Correct citation text in terminal and Gradio output
- Multithreading for OpenAI response to better handle streaming responses 
### Changed
- Refactored interfaces to own classes
- Refactored formatters to own classes
- Gradio and terminal now use same OpenAI access pattern

## [0.4.0]
### Added
- Basic Gradio chat interface with previous message history
- Pre-commit hooks for Ruff format and check
### Changed
- Coverage report now covers all files

## [0.3.0]
### Changed
- Store assistant ID locally for cleaner management
- Updated system prompt
### Fixed
- Added missing `load_dotenv()` to CLI
- Fixed issue with non-defined `._write()` command in `Settings` delete item
- Fixed function typo

## [0.2.0]
### Added
- Added `vs` command line access
- Support for setting deletion
- More graceful detection if Zotero not installed
- Cross platform Zotero detection
- Additional GHA workflows
### Changed
- OpenAI chat now correctly implements assistant
- Chat now retains threads across sessions
