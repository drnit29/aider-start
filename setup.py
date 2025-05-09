#!/usr/bin/env python3
"""
Setup para instalação do aider-start.
"""

from setuptools import setup, find_packages
import os
import re

# Lê a versão diretamente do arquivo __init__.py
with open(os.path.join('aider_start', '__init__.py'), 'r', encoding='utf-8') as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Não foi possível encontrar a versão.")

# Lê o conteúdo do README.md
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="aider-start",
    version=version,
    author="Diogo",
    author_email="seu.email@example.com",
    description="Gerenciador de perfis para o aider",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aider-start",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aider-chat>=0.18.0",
        "keyring>=23.13.1",
        "textual>=0.27.0",
        "windows-curses>=2.3.1;platform_system=='Windows'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "aider-start=aider_start.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 