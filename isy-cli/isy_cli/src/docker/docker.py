from ...globals import Constants
from ..utils.template_gen import generate_flask_template, read_project_config
from ..utils.strings import get_random_string
from ..utils.docker import *

import os
import sys
import json
import typer
from typing import cast
from click.types import Choice
from pathlib import Path
from shutil import which

app = typer.Typer()

@app.command('list')
def list_images(docker_compose_file: str = typer.Option(help='Ruta al archivo de docker-compose.yml', default='docker-compose.yml')):
    docker_file = load_compose_file(docker_compose_file)
    for service in cast(dict, docker_file['services']).keys():
        typer.echo(f'* {service}')
    return cast(dict, docker_file['services']).keys()

@app.command('up')
def up_container(
    service_name: str = typer.Option(..., help='Nombre del servicio a levantar con docker declarado en el archivo compose'),
    docker_compose_file: str = typer.Option(help='Ruta al archivo de docker-compose.yml', default='docker-compose.yml'),
    detached: bool = typer.Option(help='Indica si la imagen se ejecutará en background', default=True)):
    verify_docker_install()
    extra_params = ''
    if not service_name:
        raise Exception('service_name not valid')
    
    if service_name not in list_images(docker_compose_file=docker_compose_file):
        raise Exception('service not found in docker-compose file')

    if detached:
        extra_params += ' -d'
    os.system(f'docker-compose -f {docker_compose_file} up {service_name}{extra_params}')


@app.command('down')
def down_container(docker_compose_file: str = typer.Option(help='Ruta al archivo de docker-compose.yml', default='docker-compose.yml')):
    verify_docker_install()
    os.system(f'docker-compose -f {docker_compose_file} down')

@app.command('up-db')
def up_db_container(
    docker_compose_file: str = typer.Option(help='Ruta al archivo de docker-compose.yml', default='docker-compose.yml'),
    detached: bool = typer.Option(help='Indica si la imagen se ejecutará en background', default=True)):
    verify_docker_install()
    try:
        project_config = read_project_config()
    except:
        typer.echo('No se puedo leer la configuracion del proyecto', color=typer.colors.RED)
        raise typer.Abort()
    db_dialect = project_config['dbDialect']
    found_db = False
    service_db_name = ''
    for image in list_images(docker_compose_file=docker_compose_file):
        if str(db_dialect).lower() in str(image).lower():
            found_db = True
            service_db_name = image
            break
    if not found_db:
        raise Exception('Base de datos no encontrada en archivo docker-compose')
    
    up_container(service_name = service_db_name, docker_compose_file = docker_compose_file, detached = detached)


@app.command('configure-remote')
def configure_remote(pass_from_file: bool = typer.Option(help='Indica si la contraseña viene desde un archivo docker-pass.secret', default=False)):
    verify_docker_install()
    local_project_dir = Path(os.getcwd()).joinpath('.isy')

    is_docker_hub = typer.confirm("Su host remoto se encuentra en DockerHub?")
    if not is_docker_hub:
        docker_server = typer.prompt("Host de su repositorio de contenedores docker")
    else:
        docker_server = 'Docker-hub'
    docker_repo = typer.prompt("Nombre de su repositorio de contenedores docker")
    docker_user = typer.prompt("Usuario de su repositorio de contenedores docker")

    docker_pass = ''
    if pass_from_file:
        if not Path('docker-pass.secret').exists():
            typer.Abort()
            raise Exception('No se encuentra el archivo docker-pass.secret')
        with open('docker-pass.secret', 'r') as f:
            docker_pass = f.read()
    else:
        docker_pass = typer.prompt("Contraseña de host remoto", hide_input=True)

    if not local_project_dir.exists():
        os.mkdir(local_project_dir)
    
    with open(local_project_dir.joinpath('docker-prop.info'), 'w') as f:
        json.dump({
            "server": docker_server,
            "user": docker_user,
            "repository": docker_repo,
            "is_dockerhub": is_docker_hub
        }, f)
    
    docker_cmd_login = f'docker login {docker_server if not is_docker_hub else ""} -u {docker_user} -p {docker_pass}'
    os.system(docker_cmd_login)
    typer.echo('Se ha guardado correctamente')

@app.command('build-app')
def docker_build():
    verify_docker_install()
    docker_config = read_docker_config()
    is_docker_hub = docker_config['is_dockerhub']
    docker_server = docker_config['server']
    docker_user = docker_config['user']
    docker_repo = docker_config['repository']

    tag = typer.prompt('Nombre del tag: ', default='latest')
    complete_repo = f'{docker_user if is_docker_hub else docker_server}/{docker_repo}:{tag}'
    docker_build_cmd = f'docker build -t {complete_repo} .'
    os.system(docker_build_cmd)
    return complete_repo

@app.command('push-app')
def docker_push(pass_from_file: bool = typer.Option(help='Indica si la contraseña viene desde un archivo docker-pass.secret', default=False)):
    verify_docker_install()
    docker_cmd_login = get_cmd_login(pass_from_file)
    os.system(docker_cmd_login)

    complete_repo = docker_build()
    docker_push_cmd = f'docker push {complete_repo}'
    os.system(docker_push_cmd)

