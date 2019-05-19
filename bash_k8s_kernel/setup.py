from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='bash_k8s_kernel',
    version='1.1',
    packages=['bash_k8s_kernel'],
    description='Simple example kernel for Jupyter',
    long_description=readme,
    author_email='spapagian@ics.forth.gr',
    install_requires=[
        'jupyter_client', 'IPython', 'ipykernel',
        'kubernetes',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],
)
