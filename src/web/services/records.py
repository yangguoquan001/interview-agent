from pathlib import Path
from dataclasses import dataclass


@dataclass
class InterviewRecord:
    file_path: Path
    date: str
    topic: str
    content: str


class RecordService:
    def __init__(self, records_dir: str = "records"):
        self.records_dir = Path(records_dir)

    def get_all_records(self) -> dict[str, list[InterviewRecord]]:
        if not self.records_dir.exists():
            return {}

        records_by_date: dict[str, list[InterviewRecord]] = {}

        for date_dir in sorted(self.records_dir.iterdir(), reverse=True):
            if not date_dir.is_dir():
                continue

            date_str = date_dir.name
            records = []

            for md_file in sorted(date_dir.glob("*.md")):
                record = self._parse_record(md_file, date_str)
                if record:
                    records.append(record)

            if records:
                records_by_date[date_str] = records

        return records_by_date

    def get_record_by_path(self, file_path: str) -> str:
        path = Path(file_path)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def delete_record(self, file_path: str) -> bool:
        path = Path(file_path)
        try:
            if path.exists() and path.is_file():
                path.unlink()
                return True
            return False
        except Exception:
            return False

    def _parse_record(self, file_path: Path, date_str: str) -> InterviewRecord | None:
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            topic = "未命名"
            for line in lines:
                if line.startswith("# 面试练习记录:"):
                    topic = line.replace("# 面试练习记录:", "").strip()
                    break
            return InterviewRecord(
                file_path=file_path, date=date_str, topic=topic, content=content
            )
        except Exception:
            return None
