"""Package setup."""
import os
from glob import glob
from setuptools import setup, find_packages

sites_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sites")
sites_ini = glob(os.path.join("sites", "*.ini"))

setup(
    name="samplecmd",
    version="1.0.6",
    description="SampleCMD is a CLI application which prepares sample "
                "commands for users based on search words.",
    author="Morteza Nourelahi Alamdari",
    author_email="me@mortezana.com",
    keywords=["samplecmd", "cmd", "cli", "search"],
    license="GPLv3.0",
    url="https://github.com/mortezaipo/samplecmd/",
    packages=find_packages(),
    install_requires=['colorclass', 'lxml', 'requests'],
    data_files=[(sites_path, sites_ini)],
    include_package_data=True,
    python_requires='>=3',
    entry_points={
        "console_scripts": [
            "samplecmd=samplecmd.samplecmd:main",
        ],
    })
