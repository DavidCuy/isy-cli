# Sub-Comando Project

Este subcomando es utilizado para realizar tareas y afectaciones generales para el proyecto.

```
.
└── isy
    ├── project
    │   └── init
    │   └── configure
```

## Project commands

```isy project init```

Genera un nuevo proyecto con el cli de isy en la carpeta donde se haya ejecutado el comando. El promt nos hará una serie de preguntas para configurar nuestro proyecto relacionado con la base de datos de SQL a utilizar. Actualmente isy tiene soporte para las siguientes bases de datos:

* SQLite
* MySQL
* PostgresSQL
* Microsft SQL server

Y de igual forma sirve para la configuración del desarrollo si lo queremos trabajar en contenedores, siendo *docker* la opción para contenedores.

Al finalizar, isy nos descargará toda los archivos necesarios para llevar a cabo el proyecto con una configuración inicial lista para subir a un servidor.

El encarpetado final será algo similar a lo que se muestra acontinuación, esto puede variar de acuerdo a las variaciones seleccionadas entre la base de datos y el registro de contenedores.

```
.
├── /api/
│   ├── /app/
│   │   ├── /Controllers/
│   │   │   ├── __init__.py
│   │   │   └── ExampleController.py
│   │   ├── /Core/
│   │   │   ├── /Controllers/
│   │   │   │   └── BaseController.py
│   │   │   ├── /Data/
│   │   │   │   └── BaseModel.py
│   │   │   └── /Services/
│   │   │       └── BaseService.py
│   │   ├── /Data/
│   │   │   ├── /Enum/
│   │   │   │   ├── http_status_code.py
│   │   │   │   └── request_parts.py
│   │   │   ├── /Interfaces/
│   │   │   │   ├── PaginationResult.py
│   │   │   │   └── ResourceReference.py
│   │   │   └── /Models/
│   │   │       ├── __init__.py
│   │   │       └── Example.py
│   │   ├── /Exceptions/
│   │   │   └── APIException.py
│   │   ├── /Middlewares/
│   │   │   └── auth.py
│   │   ├── /Services/
│   │   │   ├── __init__.py
│   │   │   └── ExampleService.py
│   │   └── /Validators/
│   │       └── RequestValidator.py
│   ├── /config/
│   │   ├── database.py
│   │   └── storage.py
│   ├── /database/
│   │   └── DBConnection.py
│   ├── /routes/
│   │   ├── __init__.py
│   │   └── ExampleRouter.py
│   ├── /storage/
│   │   └── /local/
│   │       ├── .gitkeep
│   │       └── test.txt
│   ├── /utils/
│   │   ├── /notifications/
│   │   │   ├── __init__.py
│   │   │   └── firebase.py
│   │   ├── /storage/
│   │   │   ├── __init__.py
│   │   │   ├── local.py
│   │   │   └── s3.py
│   │   └── http_utils.py
│   └── __init__.py
├── /migrations/
│   ├── /versions/
│   │   └── f610bf799e52_.py
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── /templates/
│   └── /isiflask/
│       ├── controller.txt
│       ├── model.txt
│       ├── routes.txt
│       └── service.txt
├── /tests/
│   ├── messaging_notifications_test.py
│   └── storage_test.py
├── .dockerignore
├── .env.dist
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── Environment.py
├── isy_project.toml
├── README.md
└── requirements.txt
```

```isy project configure```

```
.
└── isy
    └── project
        └── configure
```

Imprime en consola la configuración actual del proyecto de isy. La salida de la consola debe ser similar a:

```
project_name = example-api
dbDialect = mysql
docker_db_enable = true
pattern_version = latest
```


```isy project install```

```
.
└── isy
    └── project
        └── install
```

Se encarga de instalar todos los paquetes necesarios para poder levantar el proyecto de isy, de igual manera en caso de que no detecte un ambiente virtual configurado, crea uno. Para esto se debe tener instalado el módulo de virtualenv de python `pip install virtualenv`

Al finalizar su ejecución, deberá crear una carpeta *venv* con todos los paquetes declarados en *requirements.txt* instalados

```isy project migrate```
```
.
└── isy
    └── project
        └── migrate

Arguments:
- apply-at-db: Bandera que indica si los cambios en los modelos debe impactar directamente en la base de datos.
```


```isy project run```
```
.
└── isy
    └── project
        └── run

Arguments:
- method: Define el método utilizado para levantar la aplicación. Sólo se permiten los valores [*flask-run*, *docker*]. Default=*flask-run*
- only-project-app: Si se selecciona docker como método, se puede especificar si sólo se debe levantar el contenedor de la app, o todos los declarados en el archivo docker-compose.
- rebuild-docker: Solo se puede utilizar con método docker. Indica si al levantar la app se debe re-construir la imagen de docker.
```