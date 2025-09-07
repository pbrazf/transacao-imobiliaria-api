from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    # Atributos obrigatórios da classe.
    API_PREFIX: str
    DATABASE_URL: str
    JWT_SEGREDO: str
    JWT_ALGORITMO: str
    JWT_MINUTOS: int

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',   # ignora variáveis que não pertencem ao modelo
    )

# Cria uma instância única da configuração
settings = Config()
