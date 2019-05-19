from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='psql_kernel',
    version='1.1',
    packages=['psql_kernel'],
    description='Simple example kernel for Jupyter',
    long_description=readme,
    install_requires=[
        'jupyter_client', 'IPython', 'ipykernel',
        'docker', 'bash_kernel'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],
)
