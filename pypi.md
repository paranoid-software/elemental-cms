# elemental CMS

Elemental is a Flask and MongoDB web CMS intended for developers.

Our main goal is to allow developers to create and maintain web portals or web applications using their preferred programming IDE like VS Code, PyCharm, Visual Studio, etc.

The main interaction with the tool takes place through its CLI, a self documented command line tool called "elemental-cms" which helps us perform deployment tasks directly from the terminal.

It relies on MongoDB to store the metadata, pages' content, snippets' content, dependencies information, and user session data.

## Setup

To install the tool, we can issue the following command:

```shell
pip install elemental-cms
```

This will install all the dependencies required for elemental-cms to work. Version 2.0.6 is compatible with:
- Flask 2.2.5
- Werkzeug 2.2.3
- Flask-Babel 2.0.0
- And other dependencies as specified in setup.py

## New in 2.0.6

- **Shell Autocomplete**: Tab completion for snippets, pages, and global-deps commands
- **Pages Diff Command**: Compare local and database versions of pages
- **Snippets Diff Command**: Compare local and database versions of snippets
- **Repository Indicators**: See which resources have local changes at a glance

To enable shell autocomplete, see the [COMPLETION.md](https://github.com/paranoid-software/elemental-cms/blob/develop/COMPLETION.md) guide.

## Running elemental-cms command for the first time

After setup, we can start using the tool like this:

![Running CLI](https://github.com/paranoid-software/elemental-cms/blob/develop/.docs-assets/run-elemental.gif?raw=true)

## Documentation

More details about the tool can be found [here](https://paranoid.software/en/elemental-cms/docs) on the official documentation portal. For version history and changes, see our [CHANGELOG](https://github.com/paranoid-software/elemental-cms/blob/develop/CHANGELOG.md).
