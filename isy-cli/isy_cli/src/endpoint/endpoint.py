from ...globals import load_config
from ..utils.folders import validate_path_not_exist
from ..utils.strings import camel_case
from ..utils.template_gen import add_code_to_module, add_file_to_module

import typer
from pathlib import Path

app = typer.Typer()

@app.command('new')
def new_endpoint(
        method: str = typer.Option(..., help='Metodo de la peticion. Valores permitidos [GET, POST, PUT, PATCH, DELETE]'),
        path: str = typer.Option(..., help='Path del endpoint.'),
        model_name: str = typer.Option(help='Nombre de un modelo existente. Si no existe, crea el service, controller y router correspondiente', default='')
    ):
    if not model_name:
        func_name = f"{method.lower()}_{path.replace('/', '_')}"
        model_name = path.split('/')[0]
    config = load_config()
    name = camel_case(model_name)
    
    routes_template_path = Path(config.template.files.endpointConf)
    routes_folder_path = Path(config.project.folders.endpoints)

    controller_template_path = Path(config.template.files.controllerEndpointConf)
    controller_folder_path = Path(config.project.folders.controllers)

    model_exists = False
    try:
        model_exists = validate_path_not_exist(path=routes_folder_path.joinpath(f'{name}Router.py'), custom_error_message=f'Ya existe una ruta con nombre: {name}', abort=False)
    except Exception as e:
        typer.echo(str(e))
    
    if not model_exists:
        service_template_path = Path(config.template.files.serviceEndpointConf)
        service_folder_path = Path(config.project.folders.services)
        add_code_to_module(service_template_path, service_folder_path, f"{name}Service", {'model_name': name})
        add_file_to_module(service_folder_path, f"{name}Service")
        
        add_code_to_module(controller_template_path, controller_folder_path, f"{name}Controller", {'model_name': name, 'func_name': func_name})

        add_code_to_module(routes_template_path, routes_folder_path, f"{name}Router", {'model_name': name, 'model_name_lower': name.lower(), 'func_name': func_name})
        add_file_to_module(routes_folder_path, f"{name}Router", f"{name.lower()}_router")
        
        index_code = Path(config.project.folders.root).joinpath('__init__.py').read_text()

        search_return = index_code.index('return app')

        block_insert_code = f"""from .routes import {name.lower()}_router
    app.register_blueprint({name.lower()}_router, url_prefix='/{name.lower()}')
    
    """

        index_code = index_code[:search_return] + block_insert_code + index_code[search_return:]
        Path(config.project.folders.root).joinpath('__init__.py').write_text(index_code)
    
    controller_text = controller_folder_path.joinpath(f'{name}Controller.py').read_text()
    controller_block_insert = f"""{controller_text}

def {func_name}(service: {name}Service):
    return build_response(HTTPStatusCode.OK.value, {{"text": "Hello World!"}})
"""
    controller_folder_path.joinpath(f'{name}Controller.py').write_text(controller_block_insert)

    router_text = routes_folder_path.joinpath(f'{name}Router.py').read_text()
    import_controller_text = f'from api.app.Controllers.{name}Controller import *'
    prepend_text = f'{import_controller_text}\n' if import_controller_text not in router_text else ''
    router_block_insert = f"""{prepend_text}{router_text}

{name.lower()}_router.route('{path.replace(model_name, '')}', methods=['{method.upper()}'], defaults={{'service': {name.lower()}_service}}) ({func_name})
"""
    routes_folder_path.joinpath(f'{name}Router.py').write_text(router_block_insert)

    typer.echo(f'La ruta {path} [{method}] se agrego correctamente!', color=typer.colors.GREEN)

