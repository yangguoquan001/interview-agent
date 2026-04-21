from pathlib import Path
from dataclasses import dataclass


@dataclass
class InterviewRecord:
    file_path: Path
    date: str
    topic: str
    content: str
    source: str


class RecordService:
    def __init__(self, records_dirs: list[str] = None):
        if records_dirs is None:
            records_dirs = ["records", "resume_records"]
        self.records_dirs = [Path(d) for d in records_dirs]

    def get_all_records(self) -> dict[str, list[InterviewRecord]]:
        records_by_date: dict[str, list[InterviewRecord]] = {}

        for records_dir in self.records_dirs:
            if not records_dir.exists():
                continue

            for date_dir in sorted(records_dir.iterdir(), reverse=True):
                if not date_dir.is_dir():
                    continue

                date_str = date_dir.name
                records = []

                for md_file in sorted(date_dir.glob("*.md")):
                    record = self._parse_record(md_file, date_str, records_dir.name)
                    if record:
                        records.append(record)

                if records:
                    if date_str not in records_by_date:
                        records_by_date[date_str] = []
                    records_by_date[date_str].extend(records)

        return dict(sorted(records_by_date.items(), reverse=True))

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

    def _parse_record(
        self, file_path: Path, date_str: str, source: str
    ) -> InterviewRecord | None:
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            topic = file_path.stem
            for line in lines:
                if line.startswith("# 面试练习记录:") or line.startswith("# 简历记录:"):
                    topic = (
                        line.replace("# 面试练习记录:", "")
                        .replace("# 简历记录:", "")
                        .strip()
                    )
                    break
            return InterviewRecord(
                file_path=file_path,
                date=date_str,
                topic=topic,
                content=content,
                source=source,
            )
        except Exception:
            return None
