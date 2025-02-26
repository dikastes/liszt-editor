# liszt_editor
This is a prototype of the data input mask for the Liszt Catalog Raisonné

## How to install

First, clone the following repositories to a directories of your choice (but outside the liszt-editor directory).

- [edwoca](https://github.com/dikastes/edwoca)
- [dmad](https://github.com/dikastes/dmad-on-django)
- [acdh-django-zotero](https://github.com/dikastes/acdh-django-zotero)

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

## Run the server

Run the server from the root directory of liszt-editor:

```{bash}
# python3 manage.py runserver
```
