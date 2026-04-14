from typing import Any, Dict

from langchain_core.messages import HumanMessage
from pathlib import Path
import json

from config import prompts
from src.schemas.states import ResumeAgentState
from src.utils.llm_fatory import get_chat_model
from src.utils.pdf_reader import read_pdf, read_text_file, get_file_hash
from src.schemas.resume_models import ResumeInfo, JobDescription


RESUME_CACHE_DIR = Path("resume_cache")


def _ensure_cache_dir():
    """确保缓存目录存在"""
    RESUME_CACHE_DIR.mkdir(exist_ok=True)


def get_cache_path(file_path: Path) -> Path:
    """获取缓存文件路径"""
    file_hash = get_file_hash(file_path)
    return RESUME_CACHE_DIR / f"{file_hash}.json"


def save_to_cache(data: Dict[str, Any], file_path: Path):
    """保存解析结果到缓存"""
    _ensure_cache_dir()
    cache_path = get_cache_path(file_path)
    cache_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_from_cache(file_path: Path) -> Dict[str, Any] | None:
    """从缓存加载解析结果"""
    cache_path = get_cache_path(file_path)
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
    return None


def parse_resume(file_path: Path) -> ResumeInfo:
    """解析简历文件"""
    if not file_path.exists():
        raise FileNotFoundError(f"简历文件不存在: {file_path}")

    cached = load_from_cache(file_path)
    if cached:
        return ResumeInfo(**cached)

    if file_path.suffix.lower() == ".pdf":
        content = read_pdf(file_path)
    else:
        content = read_text_file(file_path)

    if not content or content.startswith("Error"):
        raise ValueError(f"读取文件失败: {content}")

    llm = get_chat_model(temperature=0.3)
    response = llm.invoke(
        [
            HumanMessage(
                content=prompts.RESUME_PARSER_PROMPT_TEMPLATE.format(
                    resume_content=content
                )
            )
        ]
    )

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError as e:
        raise ValueError(f"解析LLM响应失败: {e}") from e

    save_to_cache(result, file_path)
    return ResumeInfo(**result, raw_text=content)


def parse_jd(file_path: Path) -> JobDescription:
    """解析JD文件"""
    if not file_path.exists():
        raise FileNotFoundError(f"JD文件不存在: {file_path}")

    cached = load_from_cache(file_path)
    if cached:
        return JobDescription(**cached)

    if file_path.suffix.lower() == ".pdf":
        content = read_pdf(file_path)
    else:
        content = read_text_file(file_path)

    if not content or content.startswith("Error"):
        raise ValueError(f"读取文件失败: {content}")

    llm = get_chat_model(temperature=0.3)
    response = llm.invoke(
        [
            HumanMessage(
                content=prompts.JD_PARSER_PROMPT_TEMPLATE.format(jd_content=content)
            )
        ]
    )

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError as e:
        raise ValueError(f"解析LLM响应失败: {e}") from e

    save_to_cache(result, file_path)
    return JobDescription(**result, raw_text=content)


def resume_parser_node(state: ResumeAgentState) -> Dict[str, Any]:
    """简历解析节点"""
    resume_file = state.get("resume_file")
    jd_file = state.get("jd_file")

    resume_info = parse_resume(Path(resume_file)) if resume_file else None
    job_description = parse_jd(Path(jd_file)) if jd_file else None

    return {
        "resume_info": resume_info,
        "job_description": job_description,
    }
