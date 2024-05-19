import setuptools

# with open("readme.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="experiment",
    version="0.0.1",
    author="Riccardo Galafassi",
    author_email="riccardo.galafassi@univ-lyon1.fr",
    description="A small example package",
    long_description="long_description missing",
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=['numpy','pandas','scimate'],
)