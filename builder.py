from linpgtoolbox.builder import Builder

# organize the gitignore file
# Organizer.organize_gitignore()

# 编译源代码
Builder.compile("linpgtoolbox", update_the_one_in_sitepackages=True)

# 打包上传最新的文件
# Builder.build()
# Builder.upload()
Builder.remove("src")
