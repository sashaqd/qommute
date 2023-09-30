from setuptools import setup
import setuptools

setup(
    name='Qommute',
    version='0.0.1',
    description='Optimization bus station placements and routing using quantum computing and machine learning model.',
    author= 'Samyam Lamichhane Sarthak Malla Sasha',
    url = 'https://github.com/Sasha-Malik/Qommute',
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages('src'),
    keywords=['route optimization', 'quantum computing', 'machine learning', 'bus station placement'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=['Qommute'],
    package_dir={'':'src'},
    install_requires = [
        'pytorch',
        'qiskit',
        'rustworkx',
        'pyqubo', 
        'sklearn'
    ]
)
