import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="seagate-unlocker-hainesdev",
    version="0.0.1",
    author="Dan Haines",
    author_email="unlocker@dhaines.dev",
    description="Seagate ST310014ACE diagnostics tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hainesdev/Seagate-Diagnostics-Tool/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['pyserial'],
)