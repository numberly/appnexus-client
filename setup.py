import os
import subprocess
import sys

from setuptools import setup


def get_version():
    if not os.path.isdir(".git"):
        sys.stderr.write("This does not appear to be a Git repository.")
        return ""
    return subprocess.check_output(["git", "describe", "--tags", "--always"],
                                   universal_newlines=True)[:-1]


def get_description():
    with open("README.rst") as file:
        return file.read()


setup(
    name="AppNexus-client",
    version=get_version(),
    license="MIT",
    author="numberly",
    author_email="alexys@1000mercis.com",
    description="General purpose Python client for the AppNexus API",
    long_description=get_description(),
    url="https://github.com/numberly/appnexus-client",
    download_url="https://github.com/numberly/appnexus-client/tags",
    platforms="any",
    packages=["appnexus"],
    install_requires=["requests>=2.25.0",
                      "Thingy>=0.8.3"],
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
