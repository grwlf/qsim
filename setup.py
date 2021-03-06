from setuptools import setup, find_packages
from setuptools_scm import get_version
from os import environ
from os.path import isfile, join

with open("README.md", "r") as fh:
  long_description = fh.read()

with open(join('src','qsim','version.py'), 'w') as f:
  f.write("# AUTOGENERATED!\n")
  f.write(f"__version__ = '{get_version(root='.', relative_to=__file__)}'\n")

setup(
  name="qsim",
  package_dir={'':'src'},
  package_data={"qsim": ["py.typed"]},
  zip_safe=False, # https://mypy.readthedocs.io/en/latest/installed_packages.html
  use_scm_version=True,
  author="Sergey Mironov",
  author_email="sergey.v.mironov@protonmail.com",
  description="Quantum simulator",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/grwlf/qsim",
  packages=find_packages(where='src'),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Topic :: Scientific/Engineering :: Physics",
    "Intended Audience :: Developers",
    "Development Status :: 3 - Alpha",
  ],
  python_requires='>=3.6',
  test_suite='pytest',
  tests_require=['pytest', 'pytest-mypy', 'hypothesis'],
  setup_requires=['setuptools_scm'],
  install_requires=['numpy'],
)


