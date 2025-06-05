from setuptools import setup, find_packages

setup(
    name='aider-start',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'InquirerPy',
    ],
    entry_points={
        'console_scripts': [
            'aider-start = aider_start.__main__:main',
        ],
    },
)
