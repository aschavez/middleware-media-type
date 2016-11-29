import os.path
from setuptools import setup, find_packages

package_dir = os.path.abspath(os.path.dirname(__file__))
version_file = os.path.join(package_dir, "version")
with open(version_file) as version_file_handle:
    version = version_file_handle.read()

setup(
    name = "middleware-media-type",
    version = version,
    description = "Falcon Media type middlware",
    package_dir = {"":"src"},
    packages = find_packages("src"),
    install_requires=[
        "falcon",
        "dicttoxml"
    ],
    dependency_links=[
        "git+ssh://git@git.rcp.pe:4488/devteam/falcon-exceptions.git#egg=falcon_exceptions"
    ],
    author = 'DevTeam RCP',
    author_email = 'devteam@rcp.pe',
    url = 'https://git.rcp.pe/devteam/middleware-media-type',
    keywords = ['falcon', 'media', 'type']
)
