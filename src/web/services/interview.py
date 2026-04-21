import sqlite3
import time
import uuid

from langchain_core.messages import BaseMessageChunk, HumanMessage
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite import SqliteSaver

from src.graph.workflow import create_graph, create_resume_graph
from src.schemas.states import QuestionRecord


class InterviewService:
    def __init__(self, db_path: str = "checkpoints.db", mode: str = "knowledge"):
        self.db_path = db_path
        self.mode = mode  # "knowledge" or "resume" TODO 使用enum
        self._config = None
        self._conn = None
        self._saver = None
        self._app = None

    @property
    def app(self):
        if self._app is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            serde = JsonPlusSerializer(allowed_msgpack_modules=[QuestionRecord])
            self._saver = SqliteSaver(self._conn, serde=serde)
            if self.mode == "resume":
                self._app = create_resume_graph(self._saver)
            else:
                self._app = create_graph(self._saver)
        return self._app
    
    def get_config(self, thread_id: str = None):
        if thread_id is None:
            thread_id = f"web_{int(time.time())}"
        if self._config is None:
            self._config = {"configurable": {"thread_id": thread_id}}
        return self._config

    def get_initial_input(self):
        return {
            "files_to_read": [],
            "messages": [],
            "current_file": "",
            "question": "",
            "answer": "",
            "feedback": "",
            "topic": "",
            "difficulty": "",
            "thread_id": self.get_config()["configurable"]["thread_id"],
        }

    def get_current_state(self, config=None):
        if config is None:
            config = self.get_config()
        return self.app.get_state(config)

    def stream_out_tokens(self, input_data):
        config = self.get_config()
        for msg_chunk, metadata in self.app.stream(
            input_data, config, stream_mode="messages"
        ):  
            if isinstance(msg_chunk, BaseMessageChunk):
                if hasattr(msg_chunk, "content") and msg_chunk.content:
                    yield msg_chunk.content

    def start_resume_interview(self, resume_file: str, jd_file: str):
        """开始简历面试（第一阶段：解析）"""
        thread_id = f"resume_{uuid.uuid4()}"
        config = {"configurable": {"thread_id": thread_id}}

        result = self.app.invoke(
            {
                "resume_file": resume_file,
                "jd_file": jd_file,
                "messages": [],
                "interview_mode": "resume",
            },
            config,
            interrupt_before=["questioner"],
        )

        self._config = config
        return result, config

    def generate_questions(self, config):
        """生成面试问题（第二阶段）"""
        result = self.app.invoke({}, config)
        return result

    def submit_answer(self, answer: str, config: dict = None):
        """提交回答"""
        if config is None:
            config = self.get_config()

        state = {
            "messages": [HumanMessage(content=answer)],
            "answer": answer,
        }

        result = self.app.invoke(state, config)
        return result
