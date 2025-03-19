from setuptools import setup, find_packages

setup(
    name="hieraplan",
    version="0.1.0",
    packages=find_packages(),
    package_data={"": ["*.py"]},
    include_package_data=True,
    install_requires=[
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "streamlit>=1.26.0",
        "pyvis>=0.3.2",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "graphviz>=0.20.1",
    ],
)