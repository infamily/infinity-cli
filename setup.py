from setuptools import find_packages, setup

setup(
    name='infinity-data',
    version='0.1.0',
    description='Manages data with metadata headers, that specify schemas and types.',
    url='https://github.com/infamily/infinity-data',
    author='Mindey',
    author_email='mindey@qq.com',
    license='UNLICENSE',
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires=["boltons"],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    zip_safe=False
)
