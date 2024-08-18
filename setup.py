from setuptools import setup, find_packages

setup(
  name="coastc",
  description="a little language that compiles into python",
  version="0.0.4",
  license="MIT",
  packages=find_packages(),
  entry_points={
    "console_scripts": [
      "coastc = bootstrap.coastc:main"
    ]
  }
)