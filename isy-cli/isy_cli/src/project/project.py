from ...globals import Constants, DRIVERS, SQL_PORTS_DEFAULT
from ..utils.template_gen import generate_flask_template, read_project_config
from ..utils.strings import get_random_string
from ..utils.docker import save_compose_file, load_compose_file, clean_just_app_service, clean_entrypoint, delete_compose_file

import os
import sys
import json
import typer
from typing import cast
from click.types import Choice
from pathlib import Path
from shutil import which

app = typer.Typer()

@app.command('init')
def init_project(
        pattern_type: str = typer.Option(help='Tipo de patron [sam/flask].', default='flask'),
        pattern_version: str = typer.Option(help='Version del patron.', default='latest')
    ):
    """
    Genera un nuevo proyecto con template
    """
    db_config = {
        "db_engine": None,
        "db_driver": None,
        "db_host": None,
        "db_port": None,
        "db_user": None,
        "db_pass": None,
        "db_name": None,
        "from_secret": False,
        "secret_arn": '',
    }
    docker_db_enable = False
    project_name = typer.prompt("Nombre del proyecto")
    
    if pattern_type.lower() == 'sam':

        dbChoices = Choice([
            Constants.MYSQL_ENGINE.value,
            Constants.POSTGRESQL_ENGINE.value
        ])
        db_config['from_secret'] = typer.confirm("¿Las credenciales de la base de datos se encuentra en AWS Secret Manager?")

        if db_config['from_secret']:
            db_config['secret_arn'] = typer.prompt("Escriba el arn del secreto. Revise la documentación para el formato correcto")
        
        generate_flask_template(project_name, **db_config, docker_db=docker_db_enable, pattern_type=pattern_type, pattern_version=pattern_version)
        return
    else: 
        dbChoices = Choice([
            Constants.SQLITE_ENGINE.value,
            Constants.SQLSERVER_ENGINE.value,
            Constants.MYSQL_ENGINE.value,
            Constants.POSTGRESQL_ENGINE.value
        ])
    db_config['db_engine'] = typer.prompt("Elija su motor de base de datos", "sqlite", show_choices=True, type=dbChoices)
    db_config['db_driver'] = DRIVERS[f'{Constants.MYSQL_ENGINE.value}-{pattern_type.lower()}']

    default_port = typer.confirm(f"¿Desea utilizar el port default de su driver [{SQL_PORTS_DEFAULT[db_config['db_driver']]}]?")
    db_config['db_port'] = SQL_PORTS_DEFAULT[db_config['db_driver']] if default_port else int(typer.prompt("Indique el número de su puerto de base de datos"))
    
    if db_config['db_engine'] != Constants.SQLITE_ENGINE.value:
        
        docker_db_enable = typer.confirm("¿Desea agregar configuracion de base de datos para desarrollo local en docker?") if pattern_type.lower() == 'flask' else False
        if not docker_db_enable:
            db_config['db_host'] = typer.prompt("Host de la base de datos")
        else:
            db_config['db_host'] = Constants.LOCALHOST_DB_DOCKER.value
        db_config['db_name'] = typer.prompt("Nombre de la base de datos")
        
        if docker_db_enable and db_config['db_engine'] == Constants.SQLSERVER_ENGINE.value:
            db_config['db_user'] = Constants.MSSQL_SA_USER.value
        else:
            db_config['db_user'] = typer.prompt("Usuario de la base de datos")
                
        autopassword = typer.confirm("¿Desea autogenerar la contraseña?") if docker_db_enable is True else False
        if autopassword:
            db_config['db_pass'] = get_random_string()
        else:
            db_config['db_pass'] = typer.prompt("Contraseña de la base de datos", hide_input=True)

    generate_flask_template(project_name, **db_config, docker_db=docker_db_enable, pattern_type=pattern_type, pattern_version=pattern_version)

    local_project_dir = Path(os.getcwd()).joinpath(project_name).joinpath('.isy')
    if not local_project_dir.exists():
        os.mkdir(local_project_dir)
    
    with open(local_project_dir.joinpath('project.json'), 'w') as f:
        json.dump({
            "project_name": project_name,
            "dbDialect": db_config['db_engine'],
            "docker_db_enable": docker_db_enable,
            "pattern_version": pattern_version
        }, f)
    

@app.command('configure')
def read_config():
    try:
        project_config = read_project_config()
    except:
        typer.echo('No se puedo leer la configuracion del proyecto', color=typer.colors.RED)
        raise typer.Abort()
    
    output_str = ""
    for key in project_config.keys():
        output_str += f"{key} = {project_config[key]}\n"
    
    typer.echo(output_str)


@app.command('install')
def install_project():
    python_path = __get_venv_python_path()
    typer.echo('Instalando bibliotecas')
    os.system(f'{python_path} -m pip install -r requirements.txt')
            


@app.command('migrate')
def db_migrate(apply_at_db: bool = typer.Option(help='Indica si se aplica la migración en la db', default=False)):
    python_path = __get_venv_python_path()
    __set_flask_env()
    os.system(f'{python_path} -m flask db migrate')

    if apply_at_db:
        os.system(f'{python_path} -m flask db upgrade')


@app.command('run')
def run_app(
        method: str = typer.Option(help='Método para levantar la aplicación', default='flask-run'),
        only_project_app: bool = typer.Option(help='Indica si solo se levanta la app usando docker', default=False),
        rebuild_docker: bool = typer.Option(help='Indica si solo se levanta o se construye la app usando docker', default=False)):
    if only_project_app and not (method == 'docker'):
        typer.echo('Solo se puede usar "only-docker-app" seleccionando docker como método de ejecución')
        raise typer.Abort()
    if rebuild_docker and not (method == 'docker'):
        typer.echo('Solo se puede usar "rebuild_docker" seleccionando docker como método de ejecución')
        raise typer.Abort()
    try:
        project_config = read_project_config()
    except:
        typer.echo('No se puedo leer la configuracion del proyecto', color=typer.colors.RED)
        raise typer.Abort()
    if method == 'flask-run':
        python_path = __get_venv_python_path()
        __set_flask_env()

        os.system(f'{python_path} -m flask run --host=0.0.0.0')

    elif method == 'docker':
        if which('docker-compose') is None:
            typer.echo('No se encuentra el comando docker-compose instalado en el equipo', color=typer.colors.RED)
            typer.Abort()
        try:
            extra_params = ' --build' if rebuild_docker else ''
            output_docker_filename = 'docker-compose.yml'
            if only_project_app:
                docker_file = load_compose_file()
                if docker_file is None:
                    raise Exception('Can not read docker-compose file')
                docker_file = clean_just_app_service(docker_file, project_config["project_name"])
                output_docker_filename = 'docker-compose.isy.yml'
                save_compose_file(docker_file, output_docker_filename)
            #clean_entrypoint()
            os.system(f'docker-compose -f {output_docker_filename} up {extra_params}')
        except KeyboardInterrupt:
            os.system('docker-compose down')
            if only_project_app:
                delete_compose_file()
    else:
        typer.echo('El método especificado no está permitido [flask-run, docker]')


def __set_flask_env():
    os.environ['FLASK_APP'] = 'api'
    os.environ['FLASK_RUN_HOST'] = '0.0.0.0'
    os.environ['FLASK_ENV'] = 'development'


def __verify_venv():
    if sys.prefix != sys.base_prefix:
        typer.echo('No se reconocio ambiente virtual')
        if not Path.exists(Path(os.getcwd()).joinpath('venv')):
            typer.echo('No se encontró carpeta de ambiente virtual')
            os.system('python -m venv venv')


def __get_venv_python_path():
    __verify_venv()
    return '.\\venv\\Scripts\\python' if sys.platform.lower().startswith('win') else './venv/bin/python'
