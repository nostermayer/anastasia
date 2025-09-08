"""Setup script for Anastasia temporal functionality framework."""

from setuptools import setup, find_packages
import os

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements (filtering out comments and empty lines)
requirements_path = "requirements.txt"
requirements = []
if os.path.exists(requirements_path):
    with open(requirements_path, "r", encoding="utf-8") as fh:
        requirements = [
            line.strip() 
            for line in fh 
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="anastasia",
    version="1.0.0",
    author="Nick Ostermayer", 
    author_email="nick@nickostermayer.com",
    description="A framework for adding temporal functionality to objects with time-travel capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nostermayer/anastasia",
    project_urls={
        "Bug Reports": "https://github.com/nostermayer/anastasia/issues",
        "Source": "https://github.com/nostermayer/anastasia",
        "Documentation": "https://github.com/nostermayer/anastasia#readme",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Object Brokering",
        "Topic :: Database",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10", 
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Typing :: Typed",
    ],
    keywords="temporal time-travel snapshot history versioning descriptor mixin",
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0", 
            "coverage>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "sphinx>=5.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "coverage>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            # No console scripts for this library
        ],
    },
    include_package_data=True,
    zip_safe=False,
)