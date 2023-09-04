# linpg-toolbox

Linpg-toolbox is a set of tools for managing, compiling, and uploading your own python package. It has been used within Tigeia Workshop for many years and was previously been provided as part of the Linpg Engine. To better accommodate Linpg Engine's frequent iterations work schedule, linpg-toolbox has now been split out and become available as a separate third-party package.

linpg- toolbox是一个已经在缇吉娅工坊内部使用多年的开发管理以及打包工具，过去一直作为linpg引擎的一部分提供。为了能够更好地适应linpg的高速版本迭代工作，linpg-toolbox现在被拆分出来，作为单独的第三方包提供。



# Description / 描述

The toolkit contains the following classes / 工具包包含以下程序:

| Class            | Functionalities                                              | 功能                                        |
| ---------------- | ------------------------------------------------------------ | ------------------------------------------- |
| Builder          | Automates the process of compiling and uploading your personal package. | 自动化编译并上传你个人库的流程。            |
| Organizer        | A organizing tool that organizes your gitignore file(s).     | 整理工具，可以整理你的gitignore文件。       |
| PackageInstaller | A simple tool to install, upgrade and uninstall third-party python package(s). | 第三方python库安装以及卸载工具。            |
| PyInstaller      | Generate a PyInstaller hook for your personal package.       | 为你的个人库快速生成一个PyInstaller的钩子。 |
| Zipper           | Pack and file(s) and directory(s) into a zip according to the linpg.zs script file. | 根据linpg.zs脚本打包文件和数据。            |



# Examples / 例子

All Linpg Foundation packages, including the Linpg engine and this toolkit, are currently packaged using linpg-toolkit:

目前，所有Linpg基金会旗下的所有项目，包含但不仅限于Linpg引擎和该工具包本身，都使用了该工具包进行打包：



[linpg-toolbox/builder.py]: https://github.com/LinpgFoundation/linpg-toolbox/blob/master/builder.py
[linpg/builder.py]: https://github.com/LinpgFoundation/linpg



In general, you just need to copy and paste the "builder.py" file into your project's directory and modify the parameters a little, and you are good to go.

一般情况下，您只需要将builder.py复制粘贴到你的项目的目录下并稍加修改参数即可。
