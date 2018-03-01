"""Package setup."""
from setuptools import setup, find_packages

setup(
    name="samplecmd",
    version="1.1.6",
    description="SampleCMD is a CLI application which prepares sample "
                "commands for users based on search words.",
    long_description = open("README.rst").read(),
    author="Morteza Nourelahi Alamdari",
    author_email="me@mortezana.com",
    keywords=["samplecmd", "cmd", "cli", "search", "command"],
    license="GPLv3.0",
    url="https://github.com/mortezaipo/samplecmd/",
    packages=find_packages(),
    install_requires=['colorclass', 'lxml', 'requests'],
    include_package_data=True,
    python_requires='>=3',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Linux",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "License :: OSI Approved :: GPL-v3",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Terminals",
    ],
    entry_points={
        "console_scripts": [
            "samplecmd=samplecmd.samplecmd:main",
        ],
    })
