from pydantic import BaseModel


class DbConfig(BaseModel):
    host: str
    port: int
    database: str
    user: str
    password: str


class AppConfig(BaseModel):
    port: int
    db: DbConfig
    scraper_addr: str
