from setuptools import setup, find_packages

with open("README.md","r") as f : 
    description = f.read()

setup(
    name="newberryai",
    version="0.1.0",
    author="",
    author_email="",
    description="",
    packages=find_packages(),
    install_requires=[
        "boto3",
        "requests",
        "opencv-python",
    ],
    entry_points={
        "console_scripts": [
            "newberryai=newberryai.cli:main",
        ]
    },
    long_description=description,
    long_description_content_type="text/markdown",
)
