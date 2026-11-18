from pydantic_settings import BaseSettings, SettingsConfigDict

class ConsumerSettings(BaseSettings):
    # no usamos ya localhost pq separamos el consumer del backend
    bootstrap_servers: str = "127.0.0.1:9092"  
    playback_topic: str = "looptok.playback-events"

# debemos decirle a pydantic como debe obtener y gestionar la configuración del Consumer
# Asi se puede configurar el Consumer desde Docker Compose sin modificar Python
    model_config = SettingsConfigDict(
        env_prefix="KAFKA_", #las variables de entorno deben comenzar con KAFKA_
        env_file=".env", # tambien puede obtener las variables desde un archivo .env
        extra="ignore" # ignorar todas las var del .env que no esten definidas en ConsumerSettings
    )


settings = ConsumerSettings()