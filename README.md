# isy-cli

Un cli para manejar proyectos de API con flask.

> Se recomienda la instalación de docker para tener las últimas mejoras y actualizaciones. Algunas características sólo están con docker

Se recomienda utilizar el módulo *virtualenv* para los proyectos generados

Para _windows_:
````commandline
python -m venv venv
./venv/Scripts/activate
````

Para _macOS_ o _linux_:
````commandline
python -m venv venv
source ./venv/Scripts/activate
````

Posteriormente instale el cli

````commandline
pip install isy-cli
````

Para iniciar un proyecto ejecute el siguiente comando y responda las preguntas que salgan en el prompt:

````commandline
isy project init
````

Cambie el directorio al generado en el paso anterior. Utilizando *Docker*, el proyecto se levanta utilizando el siguiente comando:

````commandline
isy docker up
````

Si no utiliza docker, necesitará ejecutar lo siguiente para instalar los paquetes necesarios para su ejecución:

```commandline
isy project install
isy project run
```

## Actualización de base de datos
En caso de que se empiecen agregar los modelos y desee mantener una sincronización con su base de datos. Debe utilizar el siguiente comando:

```commandline
isy project migrate --apply-at-db
```

La bandera `--apply-at-db` indicará si quiere impactar los cambios de los modelos en base de datos, en caso de no agregarla, sólo generará los modelos de base de datos, sin afectaciones en las tablas.


## SQLAlchemy, Alembic y Blueprint

En esta herramienta, se mezcló el uso principal de estas librerías, por lo que están a su disposición todos los comandos y estructuras de datos para el desarrollo de nuevas features.

* [SQLAlchemy](https://www.sqlalchemy.org/)
* [Alembic](https://alembic.sqlalchemy.org/en/latest/)
* [Blueprint](https://flask.palletsprojects.com/en/1.1.x/blueprints/)

## Nota para los desarrolladores

Para el desarrollo local con poetry, solo hay que agregar las siguientes líneas a tu archivo `isy_project.toml`:

```
...
...
...
[tool.poetry.dependencies]
isy = { path = "<relative_path_to_project>/isy_cli", develop = true }
```

## Comandos
Para más información de los comandos, revisa la [Wiki](https://github.com/DavidCuy/easyflask-cli/wiki/)

