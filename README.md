# liszt_editor
This is a prototype of the data input mask for the Liszt Catalog Raisonné

## How to install

First, clone the following repositories to a directories of your choice (but outside the liszt-editor directory).

- [edwoca](https://github.com/dikastes/edwoca)
- [dmad](https://github.com/dikastes/dmad-on-django)
- [acdh-django-zotero](https://github.com/dikastes/acdh-django-zotero)

For some dependencies (currently edwoca and acdh-django-zotero) you need to install the CSS framework and build the CSS files.

```{bash}
# npm install tailwindcss@^3.4
# npm install daisyui@^4.12
# npx tailwindcss -i static/<app_name>/tailwind.css -o static/<app_name>/tailwind.dist.css
```

For every dependency, build the code and `pip install` it:

```{bash}
# python3 -m build
# python3 -m pip install --user dist/<package_name>-<version>.tar.gz
```

Prepare the database from the root directory of liszt-editor:

```{bash}
# python3 manage.py makemigrations
# python3 manage.py migrate
```

You need to retrieve the .env file with the secrets in order to get access to protected resources like Zotero.
Contact the maintainer for that.

## Run the server

Run the server from the root directory of liszt-editor:

```{bash}
# python3 manage.py runserver
```

## Maintainer

In case of questions, contact Matthias Schrinner: matthias.schrinner@slub-dresden.de.
