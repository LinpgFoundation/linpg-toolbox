# linpg-toolbox

![PyPI](https://img.shields.io/pypi/pyversions/linpgtoolbox?style=for-the-badge&logo=pypi) ![PyPI](https://img.shields.io/pypi/v/linpgtoolbox?style=for-the-badge&logo=pypi) ![PyPI](https://img.shields.io/pypi/dm/linpgtoolbox?style=for-the-badge&logo=pypi)

Linpg-toolbox is a set of tools for managing, compiling, and uploading your own python package. It has been used within Linpg Foundation for many years and was previously been provided as part of the Linpg Engine. To better accommodate Linpg Engine's frequent iterations work schedule, linpg-toolbox has now been split out and become available as a separate third-party package.

linpg- toolbox是一个已经在Linpg基金会内部使用多年的开发管理以及打包工具，过去一直作为linpg引擎的一部分提供。为了能够更好地适应linpg的高速版本迭代工作，linpg-toolbox现在被拆分出来，作为单独的第三方包提供。



# Description / 描述

The toolkit contains the following classes / 工具包包含以下程序:

| Class            | Functionalities                                              | 功能                                        |
| ---------------- | ------------------------------------------------------------ | ------------------------------------------- |
| Builder          | Automates the process of compiling and uploading your personal package. | 自动化编译并上传你个人库的流程。            |
| Organizer        | A organizing tool that organizes your gitignore file(s).     | 整理工具，可以整理你的gitignore文件。       |
| PackageInstaller | A simple tool to install, upgrade and uninstall third-party python package(s). | 第三方python库安装以及卸载工具。            |
| PyInstaller      | Generate a PyInstaller hook for your personal package.       | 为你的个人库快速生成一个PyInstaller的钩子。 |



# Command line usage / 命令行

This project can be used as either a Python library or a command line utility. For command line usage, see below:

该项目既可以作为 Python 库使用，也可以作为命令行工具使用。有关命令行用法，请参阅下文：

```
$ linpgtb --help
usage: linpgtb [-h] [--compile COMPILE] [--install INSTALL] [--pack PACK] [--upload UPLOAD] [--release RELEASE] [--organize ORGANIZE] [--upgrade UPGRADE] [--zip ZIP] [--fix FIX] [--select-py SELECT_PY] [--platform] [--reinstall]

options:
  -h, --help            show this help message and exit
  --compile, -c COMPILE
                        Compile project
  --install, -i INSTALL
                        Install project
  --pack, -p PACK       Pack project
  --upload UPLOAD       Upload packed project to PyPi
  --release, -r RELEASE
                        Pack and upload project to PyPi
  --organize, -o ORGANIZE
                        Organize project
  --upgrade UPGRADE     Upgrade a pip package
  --zip ZIP             Create a source distribution
  --fix FIX             Fix certain cython related issues
  --select-py SELECT_PY
                        Select the python version
  --platform            Print current platform information
  --reinstall           Reinstall Linpg Toolbox (Debug Purpose)
```
