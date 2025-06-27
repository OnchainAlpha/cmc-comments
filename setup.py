from setuptools import setup, find_packages

setup(
    name="autocrypto_social_bot",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'selenium',
        'openai',
        'python-dotenv',
        'pandas',
        'webdriver_manager',
        'httpx',
        'requests',
        'tqdm',
        'typing-extensions',
        'colorama'
    ],
) 