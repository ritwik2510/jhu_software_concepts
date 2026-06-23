from setuptools import setup, find_packages

setup(
    name="gradcafe",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "psycopg2-binary",
        "beautifulsoup4",
        "selenium",
        "requests",
    ],
    python_requires=">=3.9",
)