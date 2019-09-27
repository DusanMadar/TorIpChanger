"""TorIpChanger package installer"""


from os import path
from setuptools import setup


def read(fname, readlines=False):
    with open(path.join(path.abspath(path.dirname(__file__)), fname)) as f:
        return f.readlines() if readlines else f.read()


requirements = read("requirements.txt", True)
requirements_server = read("requirements-server.txt", True)

setup(
    version="1.1.1",
    name="toripchanger",
    url="https://github.com/DusanMadar/TorIpChanger",
    author="Dusan Madar",
    author_email="madar.dusan@gmail.com",
    description="Python powered way to get a unique Tor IP",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    keywords="change tor ip",
    packages=["toripchanger", "tests"],
    scripts=["scripts/toripchanger_server"],
    include_package_data=True,
    test_suite="tests",
    license="MIT",
    platforms="linux",
    python_requires=">=3.6",
    install_requires=requirements,
    tests_require=requirements + requirements_server,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Natural Language :: English",
    ],
    extras_require={"server": requirements_server},
)
