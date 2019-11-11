import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="papply", # Replace with your own username
    version="0.1",
    author="Sacha Hony",
    author_email="sachahony@gmail.com",
    description="Script to run command line programs in parallel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zazaho/PAPPLY",
    scripts=['papply'],
    include_package_data=True,
    data_files=[('', ['data/papply.ini.example'])],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
)
