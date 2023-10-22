from setuptools import find_packages, setup

setup(
    name="pdftotext",
    version="0.1.0",
    description="",
    author="Roman Sorin",
    author_email="roman@romansorin.com",
    url="https://github.com/romansorin/pdf-to-text",
    license="MIT",
    install_requires=[
        "pdf2image",
        "Pillow",
        "pytesseract",
        "rapidfuzz",
        "tqdm",
    ],
    tests_require=[],
    packages=find_packages(exclude=["tests"]),
    entry_points={"console_scripts": ["pdftotext = pdftotext.cli:main"]},
    include_package_data=True,
    zip_safe=False,
)
