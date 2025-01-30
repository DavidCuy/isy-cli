# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['isyflask_cli',
 'isyflask_cli.src',
 'isyflask_cli.src.model',
 'isyflask_cli.src.project',
 'isyflask_cli.src.utils']

package_data = \
{'': ['*']}

install_requires = \
['cookiecutter>=2.1.1,<3.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'toml>=0.10.2,<0.11.0',
 'typer[all]>=0.5.0,<0.6.0',
 'typing-extensions>=4.9.0',
 'setuptools==72.1.0',
 'PyYAML==6.0.1']

entry_points = \
{'console_scripts': ['isy = isyflask_cli.cli:app']}

setup_kwargs = {
    'name': 'isyflask-cli',
    'version': '0.6.0',
    'description': 'Un cli para manejar proyectos de API con flask.',
    'author': 'David Cuy',
    'author_email': 'david.cuy.sanchez@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DavidCuy/easyflask-cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
