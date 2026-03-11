from setuptools import setup, find_packages

setup(
    name="mycelium_sdk",
    version="0.1.0",
    description="Python SDK for the Mycelium API",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.27.0",
    ],
    python_requires=">=3.8",
)
