import os
import setuptools


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        content = file.read()
    return content


setuptools.setup(
    name="evedataviewer",
    version=read("VERSION").strip(),
    description="A GUI for inspecting data contained in EVE files",
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    author="Till Biskup",
    author_email="till.biskup@ptb.de",
    url="https://www.ahf.ptb.de/",
    project_urls={
        "Documentation": "https://evedataviewer.docs.till-biskup.de/",
        "Source": "https://github.com/tillbiskup/evedataviewer",
    },
    packages=setuptools.find_packages(exclude=("tests", "docs")),
    license="GPLv3",
    keywords=[
        "data viewer",
        "eve",
        "radiometry",
        "synchrotron",
        "metrology",
        "PTB",
        "BESSY",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Development Status :: 4 - Beta",
    ],
    entry_points={
        "gui_scripts": ["evedataviewer = evedataviewer.gui.app:main"],
    },
    install_requires=[
        "pandas",
        "h5py",
        "PySide6",
        "qtbricks",
    ],
    extras_require={
        "dev": [
            "prospector",
            "pyroma",
            "bandit",
            "black",
            "pymetacode",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
            "sphinx_multiversion",
        ],
    },
    python_requires=">=3.7",
    include_package_data=True,
)
