from pathlib import Path

from config.settings import settings
from src.schemas.states import AgentState
from src.utils.files_ops import random_select_file, filter_file


def scan_repositories_node(state: AgentState) -> dict:
    """
    扫描并返回所有符合条件的知识点路径
    """
    files = []
    for repo_path in settings.FILE_DIRS:
        root = Path(repo_path)
        for file in root.rglob("*.md"):
            if filter_file(file):
                files.append(file)
    final_files = random_select_file(files)
    return {"files_to_read": final_files}