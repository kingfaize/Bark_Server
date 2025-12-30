from setuptools import setup, find_packages

setup(
    name="bark-server",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "httpx[http2]",
        "pyjwt",
        "cryptography",
        "python-dotenv",
        "streamlit",
    ],
)
