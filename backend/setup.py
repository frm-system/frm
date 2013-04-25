import os
from setuptools import setup, find_packages

is_windows = os.name == 'nt'

extra_packages = ["hiredis",
                  "py-bcrypt",
                 ] if not is_windows else []

install_requires=["bottle",
                  "pymongo",
                  "PyYAML",
                  "redis",
                  "webtest",
                  "raven",
                  "unittest-xml-reporting",
                  "coverage",
                  "jsonschema"
               ]
install_requires.extend(extra_packages)

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

packages = find_packages("src")
setup(name="fountain_backend",
      version="0.0.1", 
      author="ASD Technologies",
      author_email="admin@asdco.ru",
      description="API backend server for the fountain project",
      license = "Private",
      url = "https://bitbucket.org/asdtech/fountain",
      packages = packages, 
      package_dir = {'':'src'},
      package_data = {
        '': ['*.sh', '*.ini', '*.pem', '*.txt'],
        'configs': ['*.yaml'] },
      install_requires=install_requires,
      entry_points={
        'console_scripts':
            [
                # backend
                'backend_dev = view:main',
                'backend_tests = tests:main',
                'backend_junit = tests:main_junit',
                'wsgi.py = view:wsgi',
            ]
      },

    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "License :: Other/Proprietary License",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
        "Topic :: Multimedia :: Video :: Display",
    ],
)
