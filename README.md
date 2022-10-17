# linpg-toolbox

Linpg-toolbox is a set of tools for managing, compiling, and uploading your own package. It has been used within Tigia Workshop for many years and has always been provided as part of the linpg engine. To better accommodate Linpg Engine's frequent iterations work schedule, linpg-toolbox has now been split out and become available as a separate third-party package.

linpg- toolbox是一个已经在缇吉娅工坊内部使用多年的开发管理以及打包工具，过去一直作为linpg引擎的一部分提供。为了能够更好地适应linpg的高速迭代工作，linpg-toolbox现在被拆分出来，作为单独的第三方包提供。



# Description / 描述

The toolkit contains the following programs.

**Builder** - Automates the process of compiling and uploading your personal library.

- compiler.py - A python script that is called by the Builder. Supports multi-processing.

**Organizer** - A organizing tool that organizes your gitignore files

**Pyinstaller** - Generate a Pyinstaller template for your personal repository on the fly. Typically, the template no longer requires any further changes.

**Zipper** - Pack file and directory according to the linpg.zipscript file



工具包包含以下程序：

**Builder** - 自动化编译并上传你个人库的流程

- compiler.py - 被Builder调用的编译脚本，支持多进程

**Organizer** - 整理工具，可以整理你的gitignore文件

**Pyinstaller** - 为你的个人库快速生成一个__pyinstaller模板。一般情况下，该模板不再需要任何的变动

**Zipper** - 根据linpg.zipscript文件打包数据

