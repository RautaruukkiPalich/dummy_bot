from pydantic import BaseModel, SecretStr, Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from functools import lru_cache
import re
import os


class DatabaseConfig(BaseModel):
    host: str
    port: int
    name: str
    user: str
    password: SecretStr
    db: int = 0
    ssl_mode: str = "disable"
    max_connections: int = Field(20, validation_alias="DB_MAX_CONNECTIONS")
    timeout: int = Field(30, validation_alias="DB_TIMEOUT")
    pool_size: int = Field(10, validation_alias="DB_POOL_SIZE")

    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        json_encoders={
            SecretStr: lambda v: '********'
        }
    )

    @field_validator('port')
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v

    @field_validator('host')
    @classmethod
    def validate_host(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9\.-]+$", v):
            raise ValueError('Invalid host format')
        return v

    @field_validator('max_connections', 'timeout', 'pool_size')
    @classmethod
    def validate_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('Value must be positive')
        return v

    @property
    def url(self) -> str:
        """Полный URL с паролем - только для подключения"""
        return f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"

    @property
    def safe_url(self) -> str:
        """URL без пароля - для логов"""
        return f"postgresql+asyncpg://{self.user}:********@{self.host}:{self.port}/{self.name}"

    @property
    def dsn(self) -> str:
        """Алиас для url"""
        return self.url

    def model_dump(self, **kwargs) -> dict:
        """Скрываем пароль при сериализации"""
        data = super().model_dump(**kwargs)
        data['password'] = '********'
        data['url'] = self.safe_url
        return data


class TelegramConfig(BaseModel):
    """Структура как в Go - конфигурация Telegram"""
    token: SecretStr

    model_config = ConfigDict(
        frozen=True,
        json_encoders={
            SecretStr: lambda v: '********'
        }
    )

    @property
    def get_token(self) -> str:
        return f"{self.token.get_secret_value()}"

    @property
    def safe_token(self) -> str:
        return "*********"

    def model_dump(self, **kwargs) -> dict:
        data = super().model_dump(**kwargs)
        data['token'] = '********' if self.token else None
        return data


class RedisConfig(BaseModel):
    """Структура как в Go - конфигурация Redis"""
    host: str
    port: int
    password: Optional[SecretStr] = None
    db: int = 0
    socket_timeout: int = Field(5, validation_alias="REDIS_SOCKET_TIMEOUT")
    socket_connect_timeout: int = Field(5, validation_alias="REDIS_SOCKET_CONNECT_TIMEOUT")
    retry_on_timeout: bool = Field(True, validation_alias="REDIS_RETRY_ON_TIMEOUT")
    max_connections: int = Field(20, validation_alias="REDIS_MAX_CONNECTIONS")
    decode_responses: bool = Field(True, validation_alias="REDIS_DECODE_RESPONSES")
    health_check_interval: int = Field(15, validation_alias="REDIS_HEALTH_CHECK_INTERVAL")
    ssl: bool = Field(False, validation_alias="REDIS_SSL")

    model_config = ConfigDict(
        frozen=True,
        json_encoders={
            SecretStr: lambda v: '********'
        }
    )

    @field_validator('port')
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v

    @field_validator('db')
    @classmethod
    def validate_db(cls, v: int) -> int:
        if not 0 <= v <= 15:
            raise ValueError('Redis DB must be between 0 and 15')
        return v

    @field_validator('socket_timeout', 'socket_connect_timeout', 'max_connections', 'health_check_interval')
    @classmethod
    def validate_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('Value must be positive')
        return v

    @property
    def url(self) -> str:
        """Полный URL с паролем - для подключения"""
        protocol = "rediss" if self.ssl else "redis"
        if self.password:
            return f"{protocol}://:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.db}"
        return f"{protocol}://{self.host}:{self.port}/{self.db}"

    @property
    def safe_url(self) -> str:
        """URL без пароля - для логов"""
        protocol = "rediss" if self.ssl else "redis"
        if self.password:
            return f"{protocol}://:********@{self.host}:{self.port}/{self.db}"
        return f"{protocol}://{self.host}:{self.port}/{self.db}"

    @property
    def connection_kwargs(self) -> dict:
        """Параметры для redis.Redis()"""
        kwargs = {
            'host': self.host,
            'port': self.port,
            'db': self.db,
            'socket_timeout': self.socket_timeout,
            'socket_connect_timeout': self.socket_connect_timeout,
            'retry_on_timeout': self.retry_on_timeout,
            'max_connections': self.max_connections,
            'decode_responses': self.decode_responses,
            'health_check_interval': self.health_check_interval,
            'ssl': self.ssl
        }
        if self.password:
            kwargs['password'] = self.password.get_secret_value()
        return kwargs

    def model_dump(self, **kwargs) -> dict:
        """Скрываем пароль при сериализации"""
        data = super().model_dump(**kwargs)
        data['password'] = '********' if self.password else None
        data['url'] = self.safe_url
        return data


# ==================== ГЛАВНАЯ СТРУКТУРА КОНФИГА ====================

class AppConfig(BaseSettings):
    """Главная конфигурация - как struct в Go с вложенными структурами"""

    # Environment
    env: str = Field("development", validation_alias="ENV")
    name: str = Field("myapp", validation_alias="APP_NAME")
    version: str = "1.0.0"

    # Вложенные структуры - объявляем как Optional
    database: Optional[DatabaseConfig] = None
    redis: Optional[RedisConfig] = None
    telegram: Optional[TelegramConfig] = None

    # Pydantic V2 settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True  # Весь конфиг иммутабельный
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.database is None:
            object.__setattr__(self, 'database', DatabaseConfig(
                host=self._get_env('DB_HOST', 'localhost'),
                port=int(self._get_env('DB_PORT', '5432')),
                name=self._get_env('DB_NAME', 'app'),
                user=self._get_env('DB_USER', 'postgres'),
                password=SecretStr(self._get_env('DB_PASS', '')),
                ssl_mode=self._get_env('DB_SSL_MODE', 'disable'),
                max_connections=int(self._get_env('DB_MAX_CONNECTIONS', '20')),
                timeout=int(self._get_env('DB_TIMEOUT', '30')),
                pool_size=int(self._get_env('DB_POOL_SIZE', '10'))
            ))

        if self.redis is None:
            redis_password = self._get_env('REDIS_PASSWORD', '')
            object.__setattr__(self, 'redis', RedisConfig(
                host=self._get_env('REDIS_HOST', 'localhost'),
                port=int(self._get_env('REDIS_PORT', '6379')),
                password=SecretStr(redis_password) if redis_password else None,
                db=int(self._get_env('REDIS_DB', '0')),
                socket_timeout=int(self._get_env('REDIS_SOCKET_TIMEOUT', '5')),
                socket_connect_timeout=int(self._get_env('REDIS_SOCKET_CONNECT_TIMEOUT', '5')),
                retry_on_timeout=self._get_bool('REDIS_RETRY_ON_TIMEOUT', True),
                max_connections=int(self._get_env('REDIS_MAX_CONNECTIONS', '20')),
                decode_responses=self._get_bool('REDIS_DECODE_RESPONSES', True),
                health_check_interval=int(self._get_env('REDIS_HEALTH_CHECK_INTERVAL', '15')),
                ssl=self._get_bool('REDIS_SSL', False)
            ))

        if self.telegram is None:
            token = self._get_env('TG_TOKEN', '')
            object.__setattr__(self, 'telegram', TelegramConfig(
                token=SecretStr(token) if token else None
            ))

    @staticmethod
    def _get_env(key: str, default: str = '') -> str:
        """Безопасное получение строки из окружения"""
        return os.getenv(key, default)

    @staticmethod
    def _get_bool(key: str, default: bool = False) -> bool:
        """Получение булева значения из окружения"""
        val = os.getenv(key, str(default)).lower()
        return val in ('true', '1', 'yes', 'on', 'y', 't')

    def model_dump(self, **kwargs) -> dict:
        """Безопасная сериализация всего конфига"""
        data = super().model_dump(**kwargs)

        if data.get('database'):
            data['database']['password'] = '********'
            if hasattr(self, 'database') and self.database:
                data['database']['url'] = self.database.safe_url

        if data.get('redis'):
            data['redis']['password'] = '********' if self.redis and self.redis.password else None
            if hasattr(self, 'redis') and self.redis:
                data['redis']['url'] = self.redis.safe_url

        return data

    def __repr__(self) -> str:
        return f"AppConfig(env={self.env}, name={self.name}, version={self.version})"


# ==================== СИНГЛТОН ДЛЯ КОНФИГА ====================

@lru_cache(maxsize=1)
def get_config(env_file: Optional[str] = None) -> AppConfig:
    """Возвращает конфиг как синглтон - Go style"""
    if env_file:
        from dotenv import load_dotenv
        load_dotenv(env_file, override=True)
    return AppConfig()
