import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ubkisaas",
    version="0.0.1",
    author="Asir Muminov",
    author_email="vojt.tieg295i@gmail.com",
    description="library for receiving UBKI data from the official website and parsing them and getting features for scoring analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Asirg/ubkisaas",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "ubki"},
    packages=setuptools.find_packages(where="ubki"),
    python_requires=">=3.6",
    install_requires=[
        "xmltodict",
        "requests",
        "typing",
        "python-dotenv",
        "numpy"
    ]
)