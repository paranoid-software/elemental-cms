# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.4] - 2025-08-22

### Added
- Added repository difference indicators to `snippets list` command: shows `*` for snippets that have local changes, are missing local files, or exist locally but not in the database

## [2.0.3] - 2025-08-22

### Added
- Added snippet name validation: must be lowercase, start with letter, and contain only letters, numbers and hyphens
- Added support for using SNIPPETS_FOLDER path in snippet commands (e.g., workspace/snippets/header)
- Added documentation for snippet naming rules and management

## [2.0.2] - 2025-08-22

### Added
- Added `--all` flag to `pages publish` command to publish all pages that have draft versions

## [2.0.1] - 2025-08-22

### Fixed
- Resolved dependency conflicts with Flask-Babel by using compatible versions of Flask and Werkzeug

## [2.0.0] - 2025-08-22

### Removed
- Admin feature and web interface removed to maintain focus on CLI-driven, developer-centric workflow
- Removed `/admin` routes and associated templates
- Removed admin-related static assets

### Changed
- Updated Flask to version 2.2.5 and Werkzeug to 2.2.3 for compatibility with Flask-Babel
- Fixed dependency conflicts by pinning specific versions:
  - Flask 2.2.5 (last 2.2.x version)
  - Werkzeug 2.2.3 (compatible with Flask 2.2.5)
  - Flask-Babel 2.0.0
- Other dependencies updated to use flexible version constraints

### Notes
- This is a breaking change as it removes the admin web interface and updates major dependencies
- The `USER_IDENTITY_SESSION_KEY` configuration remains as it's used for general session management
- Core CMS functionality remains unchanged, focusing on CLI-based content management
- Dependency updates resolve the Werkzeug url_quote import issue
