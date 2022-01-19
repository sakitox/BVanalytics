# Copyright Builtvisible
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import sys

from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))


install_requires = [
    'jinja2',
    'pandas',
    'tensorflow-probability >= 0.14.0',
    'matplotlib',
    'dtw-python',
    'sklearn'
]
tests_require = [
    'pytest',
    'pytest-cov',
    'mock',
    'tox'
]
setup_requires = [
    'flake8',
    'isort'
]
extras_require = {
    'docs': [
        'ipython',
        'jupyter'
    ]
}

packages = ['SEOCausal']

_version = {}
_version_path = os.path.join(here, 'SEOCausal', '__version__.py')

with open(_version_path, 'r') as f:
    exec(f.read(), _version)

with open('README.md', 'r') as f:
    readme = f.read()

setup(
    name='SEOCausal',
    version=_version['__version__'],
    author='Builtvisible',
    author_email='akiro@builtvisible.com',
    url='https://github.com/sakitox/BVanalytics',
    description= "SEO oriented causal modeling package",
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=packages,
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_require,
    setup_requires=setup_requires,
    extras_require=extras_require,
    license='Apache License 2.0',
    keywords='SEO causal impact',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering',
    ],
    project_urls={
        'Source': 'https://github.com/sakitox/BVanalytics'
    },
    python_requires='>=3, <3.10',
    test_suite='tests'
)