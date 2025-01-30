from ...globals import load_config, Config, Constants, JSON_MAPPING_VALUE
from ..utils.folders import validate_path_not_exist, validate_path_exist
from ..utils.strings import camel_case, snake_case
from ..utils.template_gen import add_code_to_module, add_file_to_module, read_project_config

import json
import typer
from typing import cast
from pathlib import Path
from dateutil import parser
from typing_extensions import Annotated

app = typer.Typer()

@app.command('new')
def new_model(name: str = typer.Option(..., help='Nombre del nuevo modelo.'), tablename: str = typer.Option(help='Nombre de la tabla', default='same-model-name')):
    config = load_config()
    name = camel_case(name)
    tablename = camel_case(name if tablename == 'same-model-name' else tablename)
    models_folder_path = Path(config.project.folders.models)

    validate_path_not_exist(path=models_folder_path.joinpath(f'{name}.py'), custom_error_message=f'Ya existe un modelo con nombre: {name}')
    __generate_full_model_config(config, name, tablename)

    typer.echo(f'{name} se agrego correctamente!', color=typer.colors.GREEN)



@app.command('fromJson')
def new_from_json(
        name: str = typer.Option(..., help='Nombre del archivo JSON a leer. Sin extension'),
        tablename: str = typer.Option(help='Nombre de la tabla', default='same-model-name')
    ):
    """
    Crea un nuevo modelo de acuerdo con el nombre especificado y el archivo en la ruta "./templates/isyflask/json"
    """
    config = load_config()
    try:
        project_config = read_project_config()
    except:
        typer.echo('No se puedo leer la configuracion del proyecto', color=typer.colors.RED)
        raise typer.Abort()
    name = camel_case(name)
    tablename = camel_case(name if tablename == 'same-model-name' else tablename)
    json_folder_path = Path(config.project.folders.jsons)
    validate_path_exist(path=json_folder_path.joinpath(f'{name.lower()}.json'), custom_error_message=f'No se pudo encontrar el archivo {name.lower()}.json')

    try:
        model_map = cast(dict, json.loads(json_folder_path.joinpath(f'{name.lower()}.json').read_text()))
    except Exception as e:
        typer.echo('No se pudo leer el json correctamente', typer.colors.RED)
        typer.Abort()

    __generate_full_model_config(config, name, tablename)

    full_column_text = ''
    full_propmap_text = ''
    full_display_member = ''
    for key in model_map.keys():
        if isinstance(model_map[key], Constants.VALID_MODEL_TYPES.value):
            key_type = type(model_map[key]).__name__

            if key_type == Constants.JSON_STRING_DTYPE.value:
                try:
                    is_date = bool(parser.parse(model_map[key]))
                    if is_date:
                        key_type = Constants.JSON_DATETIME_DTYPE.value
                except ValueError:
                    # 'String is not datetime format'
                    pass

            data_column_line_text = f"""
    {key} = {JSON_MAPPING_VALUE[key_type].format(**{'ColumnName': camel_case(key)})}"""
            #here replace
            if key_type == Constants.JSON_STRING_DTYPE.value:
                if project_config['dbDialect'] == Constants.MYSQL_ENGINE.value:
                    data_column_line_text = data_column_line_text.replace('String', 'String(512)')
            full_column_text += data_column_line_text
            full_propmap_text += f""",
            "{key}": "{camel_case(key)}\""""
            full_display_member += f""",
            "{key}\""""
    
    models_folder_path = Path(config.project.folders.models)
    model_text = models_folder_path.joinpath(f'{name}.py').read_text()
    search_text_id = f'id = Column("Id{name}", Integer, primary_key=True)'
    search_text_propmap = f"""def property_map(self) -> Dict:
        return """ + '{' + f"""
            "id": "Id{name}\""""
    search_text_display = """def display_members(cls_) -> List[str]:
        return [
            "id\""""

    search_id = model_text.index(search_text_id) + len(search_text_id)
    search_propmap = model_text.index(search_text_propmap) + len(search_text_propmap)
    search_display = model_text.index(search_text_display) + len(search_text_display)
    
    model_text = model_text[:search_id] \
            + full_column_text \
            + model_text[search_id:search_propmap] \
            + full_propmap_text \
            + model_text[search_propmap:search_display] \
            + full_display_member \
            + model_text[search_display:]
    models_folder_path.joinpath(f'{name}.py').write_text(model_text)


    typer.echo(f'{name} se agrego correctamente!', color=typer.colors.GREEN)

def __generate_full_model_config(config: Config, name: str, tablename: str):
    models_folder_path = Path(config.project.folders.models)
    template_model_path = Path(config.template.files.model)
    add_code_to_module(template_model_path, models_folder_path, name, {'model_name': name, 'model_name_lower': name.lower(), 'table_name': tablename})
    add_file_to_module(models_folder_path, name)
    
    service_template_path = Path(config.template.files.service)
    service_folder_path = Path(config.project.folders.services)
    add_code_to_module(service_template_path, service_folder_path, f"{name}Service", {'model_name': name})
    add_file_to_module(service_folder_path, f"{name}Service")
    
    controller_template_path = Path(config.template.files.controller)
    controller_folder_path = Path(config.project.folders.controllers)
    add_code_to_module(controller_template_path, controller_folder_path, f"{name}Controller", {})
    
    routes_template_path = Path(config.template.files.endpoint)
    routes_folder_path = Path(config.project.folders.endpoints)
    add_code_to_module(routes_template_path, routes_folder_path, f"{name}Router", {'model_name': name, 'model_name_lower': name.lower()})
    add_file_to_module(routes_folder_path, f"{name}Router", f"{name.lower()}_router")
    
    index_code = Path(config.project.folders.root).joinpath('__init__.py').read_text()

    search_return = index_code.index('return app')

    block_insert_code = f"""from .routes import {name.lower()}_router
    app.register_blueprint({name.lower()}_router, url_prefix='/{name.lower()}')

    """

    index_code = index_code[:search_return] + block_insert_code + index_code[search_return:]
    Path(config.project.folders.root).joinpath('__init__.py').write_text(index_code)