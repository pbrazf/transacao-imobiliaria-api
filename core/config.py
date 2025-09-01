from pydantic_settings import BaseSettings, SettingsConfigDict # BaseSettings é quem sabe ler variáveis do ambiente (incluindo .env).


class Config(BaseSettings):
    # São os atributos obrigatórios da classe.
    API_PREFIX: str
    AUTH_BEARER_TOKEN: str
    DATABASE_URL: str

    # Pydantic v2: configurações do Settings
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',   # ignora variáveis que não pertencem ao modelo
    )

# Cria uma instância única da configuração
settings = Config()
