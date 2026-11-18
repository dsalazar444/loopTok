import redis
# redis es un sistema de almacenamiento en memoria RAM de tipo clave-valor. Valkey nace de él, siguiendo caracteristicas
# libreria redis nos permite comunicarnos desde python con un servidor redis. Dado que Valkey usa mismo protocolo que Redis, su libreria nos sirve
from uuid import UUID
from app.modules.recommender.models import preferences
# Leer y modificar las preferencias almacenadas en Valkey

# Aclaración valkey: A diferencia de PostgreSQL, Valkey no requiere definir tablas ni ejecutar migraciones para estas estructuras.
# Las claves se crean conforme tu aplicación escribe información.

class PreferencesRepository:
    def __init__(self, client: redis.Redis):
        self.client = client

    # usando el cliente, obtenemos dict de preferencias de un usuario almacenado en Valkey
    def get_preferences(self, user_id: UUID) -> preferences:
        pref = self.client.hgetall(f"user:{user_id}:preferences")

        # si no hay preferencias, se inicializa una
        if not pref:
            return {}

        return {
            category:float(affinity)
            for category, affinity in pref.items() 
        } 

    # funcion para cambiar valor de key sin tener que traer los datos de Valkey al principio
    def update_affinity(self, user_id: UUID, category: str, amount: float ) -> float:
        key = f"user:{user_id}:preferences" # si usuario no existe, lo crea

        return self.client.hincrbyfloat(key, category, amount) # guarda cambios en valkey de una vez, si no existe category, la crea

    # obtenga los n campos con mayor valor de afinidad
    def get_highests_affinity(self, user_id: UUID, n: int = 3):
        pref = self.get_preferences(user_id=user_id)

        # Ordena las claves por su valor, de forma decendente, y toma las primeras n
        top_n_categories =  sorted(
                    (category for category, affinity in pref.items() if affinity > 0),
                    key=pref.get,
                    reverse=True
                )[:n]

        return top_n_categories
