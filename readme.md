# elemental CMS

Elemental is a Flask + MongoDB Web CMS intended for use by Developers mainly.

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

The CLI includes an "init" command which will create a basic working directory structure.

Before we can issue the "init" command we have to create a config file inside a "settings" folder with at least the following content:

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

After we create the config file under the name for example default.json, we can issue the "init" command as shown below: 

```shell
elemental-cms init -c settings/default.json
```

Executing this command will create and update our .elemental metadata file setting the "configFilePath" property to "settings/default.json", and it will update the folder structure which will ends looking like this:

```lang-none
workdir
└───media    
└───settings
    └───default.json
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

To create a new page we start by issuing the "pages create" CLI command:

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

In order to push a page we must use the "pages push" command:

```shell
elemental-cms pages push -p home en
```

This will save the metadata and content into the database creating a "draft" version of the page.

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

CONFIG_FILE_NAME = os.environ.get('CONFIG_FILE_NAME', 'settings/default.json')

with open(CONFIG_FILE_NAME) as config_file:
    settings = json.load(config_file)
    cms_core_context = FlaskContext(settings['cmsCoreContext'])
    cms_db_context = MongoDbContext(settings['cmsDbContext'])
    elemental_context = ElementalContext(cms_core_context, cms_db_context)

Elemental(www, elemental_context)


if __name__ == '__main__':
    www.run(host='0.0.0.0', port=8000)
```
