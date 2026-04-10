from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra="ignore")
    
    # llm 配置
    LLM_API_KEY: str 
    LLM_BASE_URL: str
    LLM_MODEL_NAME: str

    # file 配置
    FILE_DIRS: list[str] = []
    EXCLUDED_DIRS: set[str] = {
        '.git', '.github', '.vscode', 'assets', 'images', 'img', 
        'static', 'scripts', 'utils', 'node_modules', '__pycache__',
        'tests', 'docs_config'
    }
    EXCLUDED_FILES: set[str] = {
        'README.md', 'README_zh.md', 'LICENSE', 'CONTRIBUTING.md', 
        'SUMMARY.md', '_sidebar.md', '_navbar.md', 'CHANGELOG.md',
        'TOC.md', 'AGENTS.md'
    }

settings = Settings()

