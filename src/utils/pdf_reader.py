from pathlib import Path
import hashlib


def read_pdf(file_path: Path) -> str:
    """读取PDF文件内容"""
    try:
        import PyPDF2

        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


def read_text_file(file_path: Path) -> str:
    """读取文本文件内容"""
    try:
        return file_path.read_text(encoding="utf-8")
    except Exception as e:
        try:
            return file_path.read_text(encoding="gbk")
        except Exception:
            return f"Error reading file: {str(e)}"


def get_file_hash(file_path: Path) -> str:
    """获取文件MD5哈希用于缓存"""
    import hashlib

    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()
