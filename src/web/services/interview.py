from typing import Generator, Iterator
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
import time

from src.graph.workflow import create_graph


class InterviewService:
    def __init__(self, db_path: str = "checkpoints.db"):
        self.db_path = db_path
        self._app = None
        self._config = None

    @property
    def app(self):
        if self._app is None:
            with SqliteSaver.from_conn_string(self.db_path) as saver:
                self._app = create_graph(saver)
        return self._app

    def get_config(self, thread_id: str = None):
        if thread_id is None:
            thread_id = f"web_{int(time.time())}"
        if self._config is None:
            self._config = {"configurable": {"thread_id": thread_id}}
        return self._config

    def start_new_interview(self) -> Generator[str, None, None]:
        config = self.get_config()
        initial_input = {
            "files_to_read": [],
            "messages": [],
            "current_file": "",
            "question": "",
            "answer": "",
            "feedback": "",
            "topic": "",
            "difficulty": "",
            "thread_id": config["configurable"]["thread_id"],
        }

        for event in self.app.stream(initial_input, config, stream_mode="updates"):
            for node_name, values in event.items():
                if "messages" in values:
                    last_msg = values["messages"][-1]
                    if isinstance(last_msg, AIMessage):
                        yield last_msg.content

    def get_current_state(self, config=None):
        if config is None:
            config = self.get_config()
        return self.app.get_state(config)

    def resume_interview(self) -> str:
        config = self.get_config()
        state = self.get_current_state(config)
        if state and state.next:
            for event in self.app.stream(None, config, stream_mode="updates"):
                for node_name, values in event.items():
                    if "messages" in values:
                        last_msg = values["messages"][-1]
                        if isinstance(last_msg, AIMessage):
                            return last_msg.content
        return ""

    def submit_answer(self, answer: str) -> Generator[str, None, None]:
        config = self.get_config()
        self.app.update_state(
            config, {"messages": [HumanMessage(content=answer)], "answer": answer}
        )
        for event in self.app.stream(None, config, stream_mode="updates"):
            for node_name, values in event.items():
                if "messages" in values:
                    last_msg = values["messages"][-1]
                    if isinstance(last_msg, AIMessage):
                        yield last_msg.content

    def continue_interview(self, user_input: str) -> Generator[str, None, None]:
        config = self.get_config()
        self.app.update_state(config, {"messages": [HumanMessage(content=user_input)]})
        for event in self.app.stream(None, config, stream_mode="updates"):
            for node_name, values in event.items():
                if "messages" in values:
                    last_msg = values["messages"][-1]
                    if isinstance(last_msg, AIMessage):
                        yield last_msg.content

    def next_question(self) -> Generator[str, None, None]:
        return self.continue_interview("next")
