#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='MISP_maltego',
    author='Christophe Vandeplas',
    version='1.3.4',
    author_email='christophe@vandeplas.com',
    maintainer='Christophe Vandeplas',
    url='https://github.com/MISP/MISP-maltego',
    description='Maltego transform for interacting with a MISP Threat Sharing community and with MITRE ATT&CK.',
    license='AGPLv3',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Telecommunications Industry',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python :: 3',
        'Topic :: Security',
        'Topic :: Internet',
    ],
    package_data={
        '': ['*.gif', '*.png', '*.conf', '*.mtz', '*.machine']  # list of resources
    },
    python_requires='>=3.5',
    install_requires=[
        'canari>=3.3.10,<4',
        'PyMISP>=2.4.106'
    ],
    dependency_links=[
        # custom links for the install_requires
    ]
)
