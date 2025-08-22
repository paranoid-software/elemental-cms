# elemental CMS

Elemental is a Flask and MongoDB web CMS intended for developers.

Our main goal is to allow developers to create and maintain web portals or web applications using their preferred programming IDE like VS Code, PyCharm, Visual Studio, etc.

The main interaction with the tool takes place through its CLI, a self documented command line tool called "elemental-cms" which helps us perform deployment tasks directly from the terminal.

It relies on MongoDB to store the metadata, pages' content, snippets' content, dependencies information, and user session data.

## Version Compatibility

Elemental CMS 2.0.1 is compatible with:
- Flask 2.2.5
- Werkzeug 2.2.3
- Flask-Babel 2.0.0
- Python 3.6+

For version history and changes, see our [CHANGELOG](CHANGELOG.md).

## Work in progress

- <a href="https://paranoid.software/en/elemental-cms/docs" target="_blank">Official documentation</a> construction
- Media files management on GCS module test classes
- Static files management on GCS module test classes
- Pages management module review and refactor
- Samples review and update

## To Do

- Resources names validation
- Configurations schema review
- Test coverage review
- Support for detailed comparison between local and remote resources versions
- Support for sample settings file generation

## Configuration Guide

Elemental CMS uses a JSON configuration file that defines how the CMS operates. There are two main contexts:

### Core Context (`cmsCoreContext`)

#### Basic Settings
- `DEBUG`: Enable/disable debug mode (default: false)
- `ENV`: Environment name (e.g., "development", "production")
- `SECRET_KEY`: Flask secret key for session encryption
- `SITE_NAME`: Your site's name, used in templates
- `COMPANY`: Your company name
- `CANONICAL_URL`: Base URL for your site

#### Language Settings
- `LANGUAGES`: List of supported language codes (e.g., ["en", "es"])
- `DEFAULT_LANGUAGE`: Default language code (e.g., "en")
- `LANGUAGE_MODE`: Either "single" or "multi" for language handling
  - "single": No language prefixes in URLs
  - "multi": URLs prefixed with language code (e.g., /en/about)

#### File Storage Settings
- `STATIC_FOLDER`: Local folder for static files (default: "static")
- `MEDIA_FOLDER`: Local folder for media files (default: "media")
- `STATIC_URL`: URL for static files
  - Local: "/static"
  - Cloud: "https://storage.googleapis.com/your-bucket"
- `MEDIA_URL`: URL for media files
  - Local: "/media"
  - Cloud: "https://storage.googleapis.com/your-bucket"

#### Cloud Storage (Optional)
- `STATIC_BUCKET`: GCS bucket name for static files
- `MEDIA_BUCKET`: GCS bucket name for media files
- `GOOGLE_SERVICE_ACCOUNT_INFO`: GCS service account credentials
  - Required only when using Google Cloud Storage
  - Used by CLI for file operations

#### Workspace Settings
- `GLOBAL_DEPS_FOLDER`: Folder for global dependencies (default: "workspace/global_deps")
- `PAGES_FOLDER`: Folder for page files (default: "workspace/pages")
- `SNIPPETS_FOLDER`: Folder for snippet files (default: "workspace/snippets")

#### Session Settings
- `USER_IDENTITY_SESSION_KEY`: Session key for user identity (default: "userIdentity")
- `SESSION_STORAGE_ENABLED`: Enable MongoDB session storage (default: true)
- `SESSION_TIMEOUT_IN_MINUTES`: Session timeout in minutes (default: 360)

#### Development Settings
- `DESIGN_MODE_ENABLED`: Enable local file-based content editing (default: false)
  - When true: Content is read from local files
  - When false: Content is read from MongoDB

### Database Context (`cmsDbContext`)
- `id`: Unique identifier for your MongoDB connection
- `connectionString`: MongoDB connection string
  - Format: "mongodb://username:password@hostname:port/admin?directConnection=true"
- `databaseName`: Name of the MongoDB database to use

### Understanding CLI vs Web App Settings

Elemental CMS uses two separate configuration files:

1. **CLI Settings** (`local.cli.json`):
   - Used by the `elemental-cms` command-line tool
   - Requires cloud storage configuration (`STATIC_BUCKET`, `MEDIA_BUCKET`, `GOOGLE_SERVICE_ACCOUNT_INFO`)
   - Used for content management operations (push, pull, publish)
   - Example operations that use CLI settings:
     ```shell
     elemental-cms init -c settings/local.cli.json
     elemental-cms pages push -p home en
     elemental-cms media push image.jpg
     ```

2. **Web App Settings** (`local.www.json`):
   - Used by your Flask web application
   - Focuses on serving content and handling requests
   - Does not need cloud storage credentials
   - Used when running your web application
   - Example usage:
     ```python
     CONFIG_FILEPATH = os.environ.get('CONFIG_FILEPATH', 'settings/local.www.json')
     ```

#### Key Differences:

| Setting | CLI Config | Web App Config | Notes |
|---------|------------|----------------|-------|
| `STATIC_BUCKET` | Required | Optional | CLI needs it for push/pull operations |
| `MEDIA_BUCKET` | Required | Optional | CLI needs it for media management |
| `GOOGLE_SERVICE_ACCOUNT_INFO` | Required | Not needed | Only CLI performs cloud operations |
| `STATIC_URL` | Cloud URL | Can be local | Web app can serve files locally |
| `MEDIA_URL` | Cloud URL | Can be local | Web app can serve files locally |
| `DESIGN_MODE_ENABLED` | Not used | Optional | Only affects web app behavior |

#### Example Workflow:
1. Use CLI config (`local.cli.json`) to manage content:
   ```shell
   # Push content to cloud storage
   elemental-cms push --all
   ```

2. Use Web config (`local.www.json`) to serve content:
   ```python
   # Web app serves content from local or cloud
   Elemental(www, elemental_context)
   ```

### Configuration Examples

#### Local Development

CLI Config (`local.cli.json`):
```json
{
  "cmsCoreContext": {
    "DEBUG": true,
    "ENV": "development",
    "STATIC_URL": "https://storage.googleapis.com/static-bucket",
    "MEDIA_URL": "https://storage.googleapis.com/media-bucket",
    "STATIC_BUCKET": "static-bucket",
    "MEDIA_BUCKET": "media-bucket",
    "GOOGLE_SERVICE_ACCOUNT_INFO": {
      "type": "service_account",
      "project_id": "your-project"
    },
    "DESIGN_MODE_ENABLED": false
  }
}
```

Web App Config (`local.www.json`):
```json
{
  "cmsCoreContext": {
    "DEBUG": true,
    "ENV": "development",
    "STATIC_URL": "/static",
    "MEDIA_URL": "/media",
    "DESIGN_MODE_ENABLED": true
  }
}
```

#### Production Environment

CLI Config (`production.cli.json`):
```json
{
  "cmsCoreContext": {
    "DEBUG": false,
    "ENV": "production",
    "STATIC_URL": "https://storage.googleapis.com/static-bucket",
    "MEDIA_URL": "https://storage.googleapis.com/media-bucket",
    "STATIC_BUCKET": "static-bucket",
    "MEDIA_BUCKET": "media-bucket",
    "GOOGLE_SERVICE_ACCOUNT_INFO": {
      "type": "service_account",
      "project_id": "your-project"
    }
  }
}
```

Web App Config (`production.www.json`):
```json
{
  "cmsCoreContext": {
    "DEBUG": false,
    "ENV": "production",
    "STATIC_URL": "https://storage.googleapis.com/static-bucket",
    "MEDIA_URL": "https://storage.googleapis.com/media-bucket",
    "DESIGN_MODE_ENABLED": false
  }
}
```

## Setup <a id="setup">#</a>

Once we have our project folder created and our virtual environment in place, we proceed to install Elemental CMS using pip.

```shell
pip install elemental-cms
```

The CLI includes an "init" command which will create a basic working directory structure.

Before we can issue the "init" command, we have to create a config file inside a "settings" folder with at least the following content:

```json
{
  "cmsCoreContext": {
    "DEBUG": true,
    "ENV": "development",
    "SECRET_KEY": "the-secret",
    "SITE_NAME": "Elemental CMS",
    "COMPANY": "Your company name",
    "CANONICAL_URL": "https://elemental.cms",
    "LANGUAGES": [
      "en",
      "es"
    ],
    "DEFAULT_LANGUAGE": "en",
    "LANGUAGE_MODE": "multi",
    "STATIC_FOLDER": "static",
    "MEDIA_FOLDER": "media",
    "STATIC_URL": "https://storage.googleapis.com/static-files-bucket",
    "MEDIA_URL": "https://storage.googleapis.com/media-files-bucket",
    "STATIC_BUCKET": "static-files-bucket",
    "MEDIA_BUCKET": "media-files-bucket",
    "GLOBAL_DEPS_FOLDER": "workspace/global_deps",
    "PAGES_FOLDER": "workspace/pages",
    "SNIPPETS_FOLDER": "workspace/snippets",
    "GOOGLE_SERVICE_ACCOUNT_INFO": {
      "type": "service_account",
    },
    "USER_IDENTITY_SESSION_KEY": "userIdentity",
    "SESSION_STORAGE_ENABLED": true,
    "SESSION_TIMEOUT_IN_MINUTES": 360,
    "DESIGN_MODE_ENABLED": true
  },
  "cmsDbContext": {
    "id": "your-id",
    "connectionString": "mongodb://your-username:your-pwd@your-host-name:27017/admin?directConnection=true",
    "databaseName": "elemental_playground"
  }
}
```

After we create the config file under the name for example local.cli.json, we can issue the "init" command as shown below: 

```shell
elemental-cms init -c settings/local.cli.json
```

Executing this command will create and update our .elemental metadata file setting the "configFilePath" property to "settings/local.cli.json", and it will update the folder structure which will ends looking like this:

```lang-none
workdir
└───media    
└───settings
    └───local.cli.json
└───static
└───templates
    └───base.html
└───translations
└───workspace
    └───global_deps
    └───pages
    └───snippets
└───.elemental
```

> Be aware of that in Windows OS using Visual Studio 2019 after running the init command (and any other command that modify the folders and files structure), the created files and folders will not be added to the project automaticaly.

## Creating your first page

To create a new page, we start by issuing the "pages create" CLI command:

```shell
elemental-cms pages create -p home en
```

This will create the page content file and the page spec file under the workspace/pages/en directory.

### Spec file

The spec file will have the page metadata. The structure of the file will look like this:

```json
{
    "_id": {
        "$oid": "619b8f70f065731d43fb11fc"
    },
    "name": "home",
    "language": "en",
    "title": "home page",
    "description": "",
    "isHome": false,
    "cssDeps": [],
    "jsDeps": [],
    "createdAt": {
        "$date": 1637584752066
    },
    "lastModifiedAt": {
        "$date": 1637584752066
    }
}
```

### Content file

The content file will have the HTML for the page.

```html
<div></div>
```

## Pushing a page

In order to push a page, we must use the "pages push" command:

```shell
elemental-cms pages push -p home en
```

This will save the metadata and content into the database, creating a "draft" version of the page.

## Publishing a page

Until now the new page is stored on the "drafts" repository, in order to be accessible through the web application we must publish the page by running the following command:

```shell
elemental-cms pages publish -p home en
```

## Running the app

We have created a multilanguage page and successfully published it, but we are missing our application entry point.

Since this framework is based on Flask we can create an entry point just like we will do it for any other Flask application; a simple boilerplate can be found down below:

```python
import json
import os

from elementalcms import Elemental, ElementalContext
from elementalcms.core import FlaskContext, MongoDbContext
from flask import Flask

www = Flask(__name__, template_folder='templates', static_folder='static')

CONFIG_FILEPATH = os.environ.get('CONFIG_FILEPATH', 'settings/local.www.json')

with open(CONFIG_FILEPATH) as config_file:
    settings = json.load(config_file)
    cms_core_context = FlaskContext(settings['cmsCoreContext'])
    cms_db_context = MongoDbContext(settings['cmsDbContext'])
    elemental_context = ElementalContext(cms_core_context, cms_db_context)

Elemental(www, elemental_context)


if __name__ == '__main__':
    www.run(host='0.0.0.0', port=8000)
```

Note that in order to run the app locally we need another setting file (local.www.sjon) with some minor modifications. Like the one shown below:

```json
{
  "cmsCoreContext": {
    "DEBUG": true,
    "ENV": "development",
    "SECRET_KEY": "the-secret",
    "SITE_NAME": "Elemental CMS",
    "COMPANY": "Your company name",
    "CANONICAL_URL": "https://elemental.cms",
    "LANGUAGES": [
      "en",
      "es"
    ],
    "DEFAULT_LANGUAGE": "en",
    "LANGUAGE_MODE": "multi",
    "STATIC_FOLDER": "static",
    "MEDIA_FOLDER": "media",
    "STATIC_URL": "/static",
    "MEDIA_URL": "/media",
    "GLOBAL_DEPS_FOLDER": "workspace/global_deps",
    "PAGES_FOLDER": "workspace/pages",
    "SNIPPETS_FOLDER": "workspace/snippets",
    "USER_IDENTITY_SESSION_KEY": "userIdentity",
    "SESSION_STORAGE_ENABLED": true,
    "SESSION_TIMEOUT_IN_MINUTES": 360,
    "DESIGN_MODE_ENABLED": true
  },
  "cmsDbContext": {
    "id": "your-id",
    "connectionString": "mongodb://your-username:your-pwd@your-host-name:27017/admin?directConnection=true",
    "databaseName": "elemental_playground"
  }
}
```

In this file we do not need buckets information, sinces static and media resoruces will be served locally. We do not need a Google Service Account niether because that info is needed only by the cli tool to send local files to GCS.

## Windows OS + Visual Studio 2019

In Visual Studio 2019 we have some minor challenges to get started due to "problems" related with the operative system security policies more than with the tool.

- We start by creating a Python project and adding a virtual environment
- Then visual studio offers developer terminals in at least 2 flavors:
  - **Developer PowerShell** where the environment do not get activated by default, so we must activate it by running the command:

```shell
.\.venv\Scripts\Activate.ps1
```

> Depending on your security policies this command will or will not ork. When it does not work it will show an error telling you something like: "Activate.ps1 cannot be loaded because running scripts is disabled on
this system. For more information, see about_Execution_Policies at https:/go.microsoft.com/fwlink/?LinkID=135170."

> To overcome this situation we must enable running scripts at least to the current user, following the official Microsoft documentation.

  - **Developer Command Promt** were the environment do not get activated by default, so we must activate it by running the command:

```shell
.venv\Scripts\activate
```

> In both cases we assume you create the virtual environment under the name **.venv**

Resolving this minor setbacks we can go back to the <a href="#setup">Setup</a> step and follow the getting started guide normaly.
