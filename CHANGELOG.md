# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)

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
