#!/usr/bin/env python3
"""
Setup script for CMC Automation Bot

This setup.py helps with proper package recognition by IDEs like VS Code/Pylance
and allows for proper installation of the project.
"""

from setuptools import setup, find_packages
import os

# Read README if it exists
readme_content = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        readme_content = f.read()

# Read requirements if it exists
requirements = []
if os.path.exists("requirements.txt"):
    with open("requirements.txt", "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="cmc-automation-bot",
    version="1.0.0",
    description="Automated social media bot for CoinMarketCap engagement",
    long_description=readme_content,
    long_description_content_type="text/markdown",
    author="OnchainAlpha",
    author_email="",
    url="https://github.com/OnchainAlpha/cmc-comments",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements or [
        "selenium>=4.0.0",
        "undetected-chromedriver>=3.5.0",
        "requests>=2.25.0",
        "colorama>=0.4.4",
        "python-dotenv>=0.19.0",
        "psutil>=5.8.0",
        "proxyscrape>=0.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
        ]
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "cmc-bot=run_simple_menu:main",
            "cmc-automation=autocrypto_social_bot.simplified_menu:main_menu",
        ],
    },
    package_data={
        "autocrypto_social_bot": [
            "config/*.json",
            "config/*.txt",
            "*.md",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/OnchainAlpha/cmc-comments/issues",
        "Source": "https://github.com/OnchainAlpha/cmc-comments",
        "Documentation": "https://github.com/OnchainAlpha/cmc-comments/blob/main/README.md",
    },
) 