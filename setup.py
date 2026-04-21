from setuptools import setup, find_packages

setup(
    name="magicai-godot",
    version="0.1.0",
    description="MagicAI — AI 原生 Godot 引擎工具链",
    author="leisure1994",
    packages=find_packages(),
    install_requires=["click>=8.0", "litellm>=1.0", "websockets>=12.0"],
    entry_points={"console_scripts": ["magicai=cli.magicai:cli"]},
    python_requires=">=3.10",
)
