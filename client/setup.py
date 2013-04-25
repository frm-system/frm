import os
from setuptools import setup, find_packages

is_windows = os.name == 'nt'

install_requires=[ "pycurl",
                 ]

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

packages = find_packages("src")
setup(name="fountain_client",
    version="0.0.1",
    author="ASD Technologies",
    author_email="admin@asdco.ru",
    description="Programming client for Fountain API",
    license = "Private",
    url = "https://bitbucket.org/asdtech/fountain",
    packages = packages,
    package_dir = {'':'src'},
    package_data = {
        '': ['*.sh', '*.ini', '*.pem', '*.txt'],
        'configs': ['*.yaml'] },
    install_requires=install_requires,
#    entry_points={
#        'console_scripts':
#            [
#                # backend
#                'backend_acceptance_all = runall:main',
#                ]
#    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "License :: Other/Proprietary License",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.7",
        "Topic :: Tests :: Client ",
        ],
)
