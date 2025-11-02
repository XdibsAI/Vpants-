from setuptools import setup, find_packages

setup(
    name="vpants",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "streamlit==1.28.0",
        "pandas==2.0.3", 
        "plotly==5.15.0",
        "Pillow==10.0.1",
        "altair==4.2.2",
    ],
    python_requires=">=3.8",
)
