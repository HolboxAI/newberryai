from setuptools import setup, find_packages

with open("README.md","r") as f : 
    description = f.read()

setup(
    name="newberryai",
    version="0.1.0",
    author="saurabh",
    author_email="",
    description="A package for medical scribing using AWS Transcribe for the healthcare domain",
    packages=find_packages(),
    install_requires=[
        "boto3",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "healthscribe-cli=newberryai.cli:main"
        ]
    },
    long_description=description,
    long_description_content_type="text/markdown",
)
