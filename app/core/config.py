from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    # Database Configuration
    db_user: str = "postgres"
    db_password: str = ""
    db_host: str = "localhost"
    db_port: str = "5432"
    db_name: str = "lfuportal"
    
    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    
    # Security
    allowed_hosts: List[str] = ["*"]
    cors_origins: List[str] = ["*"]
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    api_key: str = ""
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    
    # Monitoring
    sentry_dsn: str = ""
    prometheus_enabled: bool = True
    tracing_enabled: bool = True
    
    # Logging
    log_level: str = "INFO"
    
    @field_validator('db_port')
    @classmethod
    def validate_port(cls, v):
        try:
            port = int(v)
            if not 1 <= port <= 65535:
                raise ValueError("Port must be between 1 and 65535")
            return str(port)
        except ValueError:
            raise ValueError("Invalid port number")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
