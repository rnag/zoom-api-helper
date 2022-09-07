"""The setup script."""
import itertools
import pathlib

from setuptools import setup, find_packages


here = pathlib.Path(__file__).parent

package_name = 'zoom_api_helper'

packages = find_packages(include=[package_name, f'{package_name}.*'])

requires = [
    'requests',
    'backports.cached-property~=1.0.2; python_version == "3.7"',
    'typing-extensions; python_version == "3.7"',
]

test_requirements = [
    'pytest~=7.1.3',
    'pytest-cov~=3.0.0',
]

extras_require = {
   'excel': ['sheet2dict'],
}

# Ref: https://stackoverflow.com/a/71166228/10237506
extras_require['all'] = list(itertools.chain.from_iterable(extras_require.values()))


about = {}
exec((here / package_name / '__version__.py').read_text(), about)

readme = (here / 'README.rst').read_text()
history = (here / 'HISTORY.rst').read_text()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/x-rst',
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=packages,
    include_package_data=True,
    install_requires=requires,
    project_urls={
        'Documentation': 'https://zoom-api-helper.readthedocs.io',
        'Source': 'https://github.com/rnag/zoom-api-helper',
    },
    license=about['__license__'],
    # TODO add more relevant keywords as needed
    keywords=['zoom-api-helper', 'zoom', 'api', 'zoom-api', 'api-v2'],
    classifiers=[
        # Ref: https://pypi.org/classifiers/
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python'
],
    test_suite='tests',
    extras_require=extras_require,
    tests_require=test_requirements,
    zip_safe=False
)
