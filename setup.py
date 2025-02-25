from setuptools import find_packages, setup

setup(
    name='F_taste_misurazioni',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask>=2.3.2',
        'flask-jwt-extended>=4.4.4',
        'flask-marshmallow>=0.14.0',
        'flask-restx>=1.1.0',
        'flask-sqlalchemy>=3.0.2',
        'marshmallow-sqlalchemy>=0.28.1',
        'bcrypt>=4.0.1',
        'cryptography>=39.0.0',
        'redis>=4.5.5'
    ],
)