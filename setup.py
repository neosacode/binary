from setuptools import setup, find_packages

__VERSION__ = '0.1'

REQUIREMENTS = []

setup(
    name='binary',
    version=__VERSION__,
    description='Binary marketing package',
    author='Juliano Gouveia',
    author_email='juliano@neosacode.com',
    keywords='binary, neosacode',
    install_requires=REQUIREMENTS,
    packages=find_packages(exclude=[]),
    python_requires='>=3.7.4'
)
