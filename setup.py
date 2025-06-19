from setuptools import setup, find_packages

def get_requirements(file_path:str)->List[str]:
    """
    this function will give list of requriments
    """
    requirement = []
    with open(file_path, 'r') as file_obj:
        requirement=file_obj.readlines()
        requirement = [req.rstrip() for req in requirement]
        #print(requirement)
        if '-e .' in requirement:
            requirement.remove('-e .')
    return requirement



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
    install_requires=get_requirements('requirements.txt'),
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
