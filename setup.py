import setuptools

setuptools.setup(
    name="isslwings",
    author="ISSL development team",
    description="",
    packages=["isslwings"],
    install_requires=["httpx[http2]", "pytest"],
)
