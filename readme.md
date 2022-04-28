# elemental CMS

Elemental is a Flask and MongoDB based CMS intended mainly for developers.

The main interaction with the tool takes place through its CLI:

```shell
elemental-cms
```

## Work in progress

- <a href="https://paranoid-software.getoutline.com/share/a300ec8e-4bc6-47c0-aba0-fbe1f80f1623" target="_blank">Documentation</a>
- Media files management module test clasess.
- Static files management module test clasess.
- Pages management module review and refactor.

## To Do

- TBD

## Setup

Once we have our project folder created and our virtual environment on place we proceed to install Elemental CMS using pip.

```shell
pip install elemental-cms
```

The CLI includes an "init" command which will create a basic structure on the working directory.

Before we can issue an "init" command we must create a "settings" folder and at least a settings file under the name debug.json with the following information:

```json
{
  "cmsCoreContext": {
    "DEBUG": true,
    "ENV": "development",
    "SECRET": "the-secret",
    "SITE_NAME": "Elemental CMS",
    "COMPANY": "Your company name",
    "CANONICAL_URL": "https://elemental.cms",
    "LANGUAGES": [
      "en",
      "es"
    ],
    "DEFAULT_LANGUAGE": "en",
    "LANGUAGE_MODE": "multi",
    "APP_NAME": "app",
    "STATIC_FOLDER": "static",
    "MEDIA_FOLDER": "media",
    "STATIC_URL": "/static",
    "MEDIA_URL": "/media",
    "STATIC_BUCKET": "static-files-bucket",
    "MEDIA_BUCKET": "media-files-bucket",
    "GLOBAL_DEPS_FOLDER": "workspace/global_deps",
    "PAGES_FOLDER": "workspace/pages",
    "SNIPPETS_FOLDER": "workspace/snippets"
  },
  "cmsDbContext": {
    "id": "your-id",
    "hostName": "127.0.0.1",
    "portNumber": 27017,
    "databaseName": "elemental_playground",
    "username": "username",
    "password": ""
  }
}
```

After initialization, you will end with the following basic folder structure:

```lang-none
workdir
└───media    
└───settings
    └───debug.json
└───static
    └───app
└───templates
    └───base.html
└───translations
└───workspace
    └───global_deps
    └───pages
    └───snippets
└───.elemental
```

## Creating your first page

To create a new page we start by issuing the pages CLI command like this:

```shell
elemental-cms pages create -p home en
```

This will create the page content file and the page spec file under the workspace/pages/en directory.

### Spec file

The spec file has the page metadata which can be then be pushed to the database in order to make the page available in the CMS.

The structure of the spec file can be seen below:

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

The content file will have the HTML for the page. After the create command execution it will have a simple html like the following:

```html
<div>This a new page.</div>
```

## Pushing a page

In order to push a page we must use the pages push command which can be called like this:

```shell
elemental-cms pages push -p home en
```

This will send the metadata and content to the database and create a "draft" version of the page.

## Publishing a page

Until now the new page is stored on the "drafts" repository, in order to be accessible through the web application we must publish the page by running the following command:

```shell
elemental-cms pages publish -p home en
```

## Running the app

Until now, we have created a multilanguage page and successfully published it, but we are missing our application entry point.

Since this framework is based on Flask we must create a simple  entry point as we will do it for any Flask application; a simple boilerplate can be found down below:

```python
import json
import os

from elementalcms import Elemental, ElementalContext
from elementalcms.core import FlaskContext, MongoDbContext
from flask import Flask

www = Flask(__name__, template_folder='templates', static_folder='static')

CONFIG_FILE_NAME = os.environ.get('CONFIG_FILE_NAME', 'settings/debug.json')

with open(CONFIG_FILE_NAME) as config_file:
    settings = json.load(config_file)
    cms_core_context = FlaskContext(settings['cmsCoreContext'])
    cms_db_context = MongoDbContext(settings['cmsDbContext'])
    elemental_context = ElementalContext(cms_core_context, cms_db_context)

Elemental(www, elemental_context)


if __name__ == '__main__':
    www.run(host='0.0.0.0', port=8000)
```
