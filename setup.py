import os
import pathlib
import setuptools

HERE = pathlib.Path(__file__).parent

LONG_DESCRIPTION = (HERE / "pypi.md").read_text()


REQUIREMENTS = [
    'Flask>=2.0.2',
    'pycountry==20.7.3',
    'pymongo>=3.12.1',
    'cloup==0.12.1',
    'deepdiff==5.6.0',
    'Flask-Babel==2.0.0',
    'google-cloud-storage>=2.3.0',
]


def read(rel_path: str) -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with open(os.path.join(here, rel_path)) as fp:
        return fp.read()


def get_version(rel_path: str) -> str:
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            # __version__ = "0.9"
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="elemental-cms",
    version=get_version("elementalcms/__init__.py"),
    author="Paranoid Software",
    author_email="info@paranoid.software",
    license="MPL-2.0",
    description="Flask + MongoDB Web CMS for Developers.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url='https://github.com/paranoid-software/elemental-cms',
    packages=setuptools.find_packages(exclude=['tests*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS,
    include_package_data=True,
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'elemental-cms=elementalcms.management:cli'
        ]
    }
)
