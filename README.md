# linpg-toolbox

![Python versions](https://img.shields.io/pypi/pyversions/linpgtoolbox?style=for-the-badge&logo=pypi) ![PyPI version](https://img.shields.io/pypi/v/linpgtoolbox?style=for-the-badge&logo=pypi) ![Downloads](https://img.shields.io/pypi/dm/linpgtoolbox?style=for-the-badge&logo=pypi)

Linpg-toolbox is a set of tools for managing, compiling, and uploading your own python package. It has been used within Linpg Foundation for many years and was previously provided as part of the Linpg Engine. To better accommodate Linpg Engine's frequent iterations work schedule, linpg-toolbox has now been split out and become available as a separate third-party package.

linpg-toolbox是一个已经在Linpg基金会内部使用多年的开发管理以及打包工具，过去一直作为linpg引擎的一部分提供。为了能够更好地适应linpg的高速版本迭代工作，linpg-toolbox现在被拆分出来，作为单独的第三方包提供。

# Installation / 安装

```bash
pip install linpgtoolbox
```

# Description / 描述

The toolkit contains the following classes / 工具包包含以下程序:

| Class            | Functionalities                                              | 功能                                        |
| ---------------- | ------------------------------------------------------------ | ------------------------------------------- |
| Builder          | Automates the process of compiling and uploading your personal package. | 自动化编译并上传你个人库的流程。            |
| Organizer        | An organizing tool that formats JSON and .gitignore files, with directory-level support that respects .gitignore patterns, or organizes your gitignore file(s). | 整理工具，可以格式化JSON和.gitignore文件，支持目录级别整理并遵循.gitignore规则，也可以整理你的gitignore文件。 |
| PackageInstaller | A simple tool to install, upgrade and uninstall third-party python package(s). | 第三方python库安装以及卸载工具。            |
| PyInstaller      | Generate a PyInstaller hook for your personal package.       | 为你的个人库快速生成一个PyInstaller的钩子。 |
| ImageResizer     | Resize images by exact dimensions or percentage via CLI.     | 通过命令行按精确尺寸或百分比调整图片大小。  |

# Command line usage / 命令行

This project can be used as either a Python library or a command line utility. For command line usage, see below:

该项目既可以作为 Python 库使用，也可以作为命令行工具使用。有关命令行用法，请参阅下文：

```text
$ linpgtb --help
usage: linpgtb [-h] [--compile COMPILE] [--install INSTALL] [--pack PACK] [--upload UPLOAD] [--release RELEASE] [--organize ORGANIZE] [--upgrade UPGRADE] [--zip ZIP] [--fix FIX] [--select-py SELECT_PY] [--show-compile-messages] [--platform] [--resize RESIZE] [--size SIZE] [--output OUTPUT] [--reinstall] [--check-update]

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
  --show-compile-messages
                        Show compile messages instead of progress bar
  --platform            Print current platform information
  --resize RESIZE       Resize an image file
  --size SIZE           Target size: WxH, N%, Wx (width only), or xH (height only)
  --output OUTPUT       Output path for resized image
  --reinstall           Reinstall Linpg Toolbox (Debug Purpose)
  --check-update        Check if a newer version is available on PyPI
```

> **Note:** Image resizing requires Pillow. Install it with `pip install linpgtoolbox[images]`.
