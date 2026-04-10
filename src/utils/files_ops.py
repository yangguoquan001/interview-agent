import random

from pathlib import Path

from config.settings import settings


def filter_file(file_path: Path) -> bool:
    """
    判断一个文件是否是高质量的知识点 md
    """
    # 1. 基本检查
    if not file_path.suffix.lower() == ".md":
        return False

    # 2. 检查文件名是否在黑名单
    if file_path.name in settings.EXCLUDED_FILES:
        return False

    # 3. 检查是否是隐藏文件
    if file_path.name.startswith("."):
        return False

    # 4. 检查路径中是否包含被排除的目录
    if any(part in settings.EXCLUDED_DIRS for part in file_path.parts):
        return False

    return True


def random_select_file(files: list, k: int = 1) -> list:
    return random.sample(files, k=min(k, len(files)))
