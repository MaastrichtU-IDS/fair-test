#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    version='0.0.6',
    name='fair-test',
    license='MIT',
    license_files = ('LICENSE'),
    description='A library to build and deploy FAIR metrics tests APIs that can be used by FAIR evaluation services supporting the FAIRMetrics specifications, such as FAIR enough and the FAIR evaluator.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    
    author='Vincent Emonet',
    author_email='vincent.emonet@gmail.com',
    maintainer='Vincent Emonet',
    maintainer_email='vincent.emonet@gmail.com',
    
    url='https://maastrichtu-ids.github.io/fair-test',
    download_url='https://github.com/MaastrichtU-IDS/fair-test/releases',
    
    packages=find_packages(),
    include_package_data=True,
    # package_dir={'rdflib_endpoint': 'rdflib_endpoint'},
    # package_data={'fair_test': ['fair_test/*.html']},

    python_requires='>=3.7.0',
    install_requires=open("requirements.txt", "r").readlines(),
    tests_require=['pytest==5.2.0'],
    # setup_requires=['pytest-runner'],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords=[
        "FAIR",
        "test",
        "evaluation",
        "API",
    ],
    project_urls={
        "Issues": "https://github.com/MaastrichtU-IDS/fair-test/issues",
        "Source Code": "https://github.com/MaastrichtU-IDS/fair-test",
        "CI": "https://github.com/MaastrichtU-IDS/fair-test/actions",
        "Releases": "https://github.com/MaastrichtU-IDS/fair-test/releases"
    },
)
