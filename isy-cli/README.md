# isyflask-cli

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
pip install isyflask-cli
````

Para iniciar un proyecto ejecute el siguiente comando y responda las preguntas que salgan en el prompt:

````commandline
isyflask-cli project init
pip install -r requirements.txt
````

Cambie el directorio al generado en el paso anterior. Utilizando *Docker*, el proyecto se levanta utilizando el siguiente comando:

````commandline
docker-compose up
````

Si no utiliza docker, necesitará ejecutar lo siguiente:

_Windows_:
```
python -m venv venv
source ./venv/Scripts/activate

set FLASK_APP=api
set FLASK_RUN_HOST=0.0.0.0
set FLASK_ENV=development 

flask db migrate
flask db upgrade
flask run --host=0.0.0.0
```

_Mac_ o _Linux_:
```
python -m venv venv
./venv/Scripts/activate

export FLASK_APP=api
export FLASK_RUN_HOST=0.0.0.0
export FLASK_ENV=development

flask db migrate
flask db upgrade
flask run --host=0.0.0.0
```

## Comandos

```
.
└── isy/
    ├── project/
    │   └── init
    └── model/
        └── new
```

```isy project init```

Como se mostró anteriormente este comando nos sirve para inicializar un proyecto con el cli de isyflask.
El promt nos hará una serie de preguntas para configurar nuestro proyecto relacionado con la base de datos de SQL a utilizar. Actualmente isy tiene soporte para las siguientes bases de datos:

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
├── isyflask_project.toml
├── README.md
└── requirements.txt
```

```isy model new```

Con este comando se creará el modelo para la definicion del proyecto, por lo que creará el servicio, el controlador y el ruteo correspondiente.

Se creará los archivos correspondientes con el siguiente formato en las ubicaciones:

* api/app/Data/Models/_ModelName_.py
* api/app/Data/Services/_ModelName_ Service.py
* api/app/Controllers/_ModelName_ Controller.py
* api/routes/_ModelName_ Router.py

Así como moficar los siguientes archivos para el import y ruteo correspondiente:

* api/app/Data/Models/__ init__.py
* api/app/Data/Services/__ init__.py
* api/app/Controllers/__ init__.py
* api/routes/__ init__.py
* api/__ init__.py

## Modelos, la base de todo

Como se indicó anteriormente, esta estructura se basa para funcionar totalmente en modelos.

Un modelo básicamente es la representación en una clase de una estructura de datos (una tabla de una DB relacional en este caso). El cuál tiene una estructura similar a como se muestra a continuación, destacando las partes de los métodos de clases que nos serán útiles posteriormente,

```python
from typing import Any, Dict, List
from sqlalchemy import Column, Integer, String
from ...Core.Data.BaseModel import BaseModel

class ModelName(BaseModel):
    """ Table ModelNames Database model

    Args:
        BaseModel (ORMClass): Parent class

    Returns:
        ModelName: Instance of model
    """
    __tablename__ = 'ModelNames'    # Nombre de la tabla en la DB
    id = Column("IdModelName", Integer, primary_key=True)
    .
    .                               # Aquí van todas las propiedades (columnas) de nuestro modelo/tabla
    .

    
    # Como se llamará nuestra ruta desde API
    model_path_name = "modelname"
    # Nombre de las propiedades a las que se les podrá aplicar filtros
    filter_columns = []
    # Nombre de las relaciones de este modelo con otros (ORM)
    relationship_names = []
    # Nombre delas propiedades a las que se les podrá hacer búsqueda con el método LIKE %search%
    search_columns = []
    

    # Mapeo de los nombres de propiedades con la respuesta del API
    def property_map(self) -> Dict:
        return {
            "id": "IdModelName"
        }
    
    # Propiedades que se mostrarán en la respuesta del API
    @classmethod
    def display_members(cls_) -> List[str]: 
        return [
            "id"
        ]

    # Reglas de validaciones del modelo antes de guardar en la DB (Revisar Validators)
    @classmethod
    def rules_for_store(cls_) -> Dict[str, List[Any]]:
        return {
            
        }

    # Método que se ejecuta antes de guardar un registro en la base de datos
    def before_save(self, sesion: Session, *args, **kwargs):
        pass
    
    # Método que se ejecuta después de guardar un registro en la base de datos
    def after_save(self, sesion: Session, *args, **kwargs):
        pass

    # Método que se ejecuta antes de actualizar un registro en la base de datos
    def before_update(self, sesion: Session, *args, **kwargs):
        pass

    # Método que se ejecuta después de actualizar un registro en la base de datos
    def after_update(self, sesion: Session, *args, **kwargs):
        pass
    
    # Método que se ejecuta antes de eliiminar un registro en la base de datos
    def before_delete(self, sesion: Session, *args, **kwargs):
        pass

    # Método que se ejecuta después de eliminar un registro en la base de datos
    def after_delete(self, sesion: Session, *args, **kwargs):
        pass
```

## SQLAlchemy, Alembic y Blueprint

En esta herramienta, se mezcló el uso principal de estas librerías, por lo que están a su disposición todos los comandos y estructuras de datos para el desarrollo de nuevas features.

* [SQLAlchemy](https://www.sqlalchemy.org/)
* [Alembic](https://alembic.sqlalchemy.org/en/latest/)
* [Blueprint](https://flask.palletsprojects.com/en/1.1.x/blueprints/)



