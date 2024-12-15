import glob
import os
import shutil
from subprocess import check_call

# get the current folder path
CURRENT_DIR_ABS: str = os.path.dirname(__file__)
# get the parent folder path
PARENT_DIR_ABS: str = os.path.dirname(CURRENT_DIR_ABS)
# the name of the parent folder
_FOLDER_NAME: str = os.path.basename(PARENT_DIR_ABS)
# a temporary folder for storing a copy
_CACHE_PATH: str = os.path.join(CURRENT_DIR_ABS, _FOLDER_NAME)
# the dist folder
_DIST_DIR: str = os.path.join(CURRENT_DIR_ABS, "dist")

# creating a copy for operations
if os.path.exists(_CACHE_PATH):
    shutil.rmtree(_CACHE_PATH)
shutil.copytree(
    PARENT_DIR_ABS,
    _CACHE_PATH,
    ignore=shutil.ignore_patterns(
        ".git", "__pycache__", ".mypy_cache", "docker", ".github", ".vscode"
    ),
)

# only support python 3.11 -> 3.13
for i in range(11, 14):
    # create a docker file for current python version
    with open(os.path.join(CURRENT_DIR_ABS, "Dockerfile"), "r") as f:
        _content: str = f.read()
    _content = _content.replace("PYTHON_VERSION_MINOR", str(i))
    Dockerfile_new_path: str = os.path.join(CURRENT_DIR_ABS, f"Dockerfile_3{i}")
    with open(Dockerfile_new_path, "w") as f:
        f.write(_content)

    # run the image to obtain compiled linux package
    IMAGE_NAME: str = f"{_FOLDER_NAME}-image-{i}"
    check_call(("docker", "build", "-t", IMAGE_NAME, "-f", Dockerfile_new_path, "."))
    check_call(("docker", "run", "--name", IMAGE_NAME, IMAGE_NAME))
    check_call(
        (
            "docker",
            "cp",
            f"{IMAGE_NAME}:/app/linpgtoolbox/dist",
            os.path.join(CURRENT_DIR_ABS, "."),
        )
    )
    check_call(("docker", "rm", IMAGE_NAME))
    check_call(("docker", "rmi", IMAGE_NAME))
    os.remove(Dockerfile_new_path)

    # get the compiled windows package
    check_call(("py", f"-3.{i}", "-m", "linpgtoolbox.cli", "-c", "."), cwd=_CACHE_PATH)
    check_call(("py", f"-3.{i}", "-m", "linpgtoolbox.cli", "-p"), cwd=_CACHE_PATH)
    for p in glob.glob(os.path.join(_CACHE_PATH, "dist", "*.whl")):
        shutil.copy2(p, _DIST_DIR)

# create the source distribution
check_call(("py", "-m", "linpgtoolbox.cli", "--zip", "."), cwd=_CACHE_PATH)
for p in glob.glob(os.path.join(_CACHE_PATH, "dist", "*")):
    shutil.copy2(p, _DIST_DIR)

# remove cache folder
shutil.rmtree(_CACHE_PATH)
