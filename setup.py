from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="newberryai",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    author="Saurabh Patil, Jaideepsinh Dabhi, Harsh Langaliya",
    author_email="jaideep@newberry.ai",
    description="NewberryAI Python Package",
    packages=find_packages(),
    install_requires=[
        "boto3",
        "requests",
        "pytest",
        "opencv-python",
        "gradio"
    ],
    entry_points={
        "console_scripts": [
            "newberryai=newberryai.cli:main",
        ]
    },
    url="https://github.com/HolboxAI/newberryai",
    long_description=description,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
