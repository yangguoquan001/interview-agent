import sqlite3
import time

from langchain_core.messages import BaseMessageChunk
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite import SqliteSaver

from src.graph.knowledge_graph import create_knowledge_graph
from src.graph.resume_graph import create_resume_graph
from src.schemas.enums import InterviewMode
from src.schemas.states import QuestionRecord


class InterviewService:
    def __init__(self, db_path: str = "checkpoints.db", mode: InterviewMode = InterviewMode.KNOWLEDGE):
        self.db_path = db_path
        self.mode = mode
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
            if self.mode == InterviewMode.RESUME:
                self._app = create_resume_graph(self._saver)
            else:
                self._app = create_knowledge_graph(self._saver)
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


