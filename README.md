# liszt_editor
This is a prototype of the data input mask for the Liszt Catalog Raisonné

## How to install

Make sure python3 is installed. Run the install script: 

```{bash}
# ./install.bash
```

After everything is done, apply migrations:

```{bash}
# bin/python3 manage.py migrate
```

## Run the server

Run the server from the root directory of liszt-editor:

```{bash}
# bin/python3 manage.py runserver
```

Alternatively run: 
```{bash}
# source bin/activate
# python3 manage.py runserver
``` 

## Maintainer

In case of questions, contact Matthias Schrinner: matthias.schrinner@slub-dresden.de.
