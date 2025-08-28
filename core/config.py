from pydantic_settings import BaseSettings # BaseSettings é quem sabe ler variáveis do ambiente (incluindo .env).


class Config(BaseSettings):
    # São os atributos obrigatórios da classe.
    API_PREFIX: str
    AUTH_BEARER_TOKEN: str
    DATABASE_URL: str

	# Padrão pudantic: “Leia variáveis também desse arquivo .env na raiz do projeto”
    class Config:
        env_file = '.env'
        
# Cria uma instância única da configuração
settings = Config()
