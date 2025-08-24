#!/usr/bin/env python
"""
Setup script for MCP Diagram Server
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcp-diagram-server",
    version="0.1.0",
    author="AI Workspace",
    author_email="workspace@example.com",
    description="MCP server for creating and manipulating Mermaid diagrams",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ai-workspace/mcp-diagram-server",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "mcp[cli]>=1.2.0",
        "aiofiles>=23.0.0",
        "pydantic>=2.0.0",
        "jinja2>=3.1.0",
        "PyYAML>=6.0.0",
        "Pillow>=10.0.0",
        "cairosvg>=2.7.0",
        "playwright>=1.40.0",
        "watchdog>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "mcp-diagram-server=main:main",
        ],
    },
)
