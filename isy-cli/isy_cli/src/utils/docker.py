import os
import yaml
import typer
import json
from typing import cast
from shutil import which
from pathlib import Path
from .folders import delete_file
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def load_compose_file(path='./docker-compose.yml'):
    docker_config = None
    with open(path, 'r') as f:
        docker_config = yaml.load(f, Loader=Loader)
    return docker_config


def save_compose_file(config: dict, path='./docker-compose.isy.yml', default_flow_style=False):
    with open(path, 'w') as f:
        yaml.dump(config, f, Dumper=Dumper, default_flow_style=default_flow_style)
    return True

def delete_compose_file(path='./docker-compose.isy.yml'):
    delete_file(src=path)

def clean_just_app_service(docker_config: dict, app_name):
    docker_app_name = str(app_name).lower().replace(' ', '').replace('-', '').replace('_', '')
    docker_services = cast(dict, docker_config['services']).copy()
    app_service_name_found = False
    for service in cast(dict, docker_config['services']).keys():
        if docker_app_name == service:
            app_service_name_found = True
        else:
            cast(dict, docker_services).pop(service)
    if not app_service_name_found:
        raise Exception(f'Project name [{docker_app_name}] not found in docker-compose file services')
    
    try:
        cast(dict, docker_services[docker_app_name]).pop('depends_on')
    except Exception as e:
        typer.echo(str(e))
    docker_services[docker_app_name]['environment']['DB_HOST'] = 'localhost'
    docker_config['services'] = docker_services
    return docker_config

def clean_entrypoint(path='./entrypoint.sh'):
    entrypoint_txt = None
    try:
        with open(path, 'r') as f:
            entrypoint_txt = f.read()
    
        new_text = "\n".join(entrypoint_txt.splitlines())
        with open(path, 'w+') as f:
            f.write(new_text)
        typer.echo(new_text)
    except Exception as e:
        typer.echo(e, color=typer.colors.RED)    

def verify_docker_install():
    if which('docker') is None:
        typer.echo('No se encuentra el comando docker instalado en el equipo', color=typer.colors.RED)
        typer.Abort()
        raise Exception('Docker not installed')
    if which('docker-compose') is None:
        typer.echo('No se encuentra el comando docker-compose instalado en el equipo', color=typer.colors.RED)
        typer.Abort()
        raise Exception('docker-compose not installed')


def read_docker_config():
    local_project_dir = Path(os.getcwd()).joinpath('.isy')
    if not local_project_dir.joinpath('docker-prop.info').exists():
        return None
    try:
        with open(local_project_dir.joinpath('docker-prop.info'), 'r') as f:
            json_file = json.loads(f.read())
    except:
        return None
    return json_file


def get_cmd_login(pass_from_file: bool) -> str:
    docker_config = read_docker_config()
    if docker_config is None:
        raise Exception('Error at read docker-config file')
    is_docker_hub = docker_config['is_dockerhub']
    docker_server = docker_config['server']
    docker_user = docker_config['user']

    docker_pass = ''
    if pass_from_file:
        if not Path('docker-pass.secret').exists():
            typer.Abort()
            raise Exception('No se encuentra el archivo docker-pass.secret')
        with open('docker-pass.secret', 'r') as f:
            docker_pass = f.read()
    else:
        docker_pass = typer.prompt("Contraseña de host remoto", hide_input=True)

    return f'docker login {docker_server if not is_docker_hub else ""} -u {docker_user} -p {docker_pass}'
