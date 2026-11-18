import redis
from app.modules.recommender.schema import KafkaEvent, PlaybackEventType, AbandonReason
from app.modules.recommender.repository.preferences import PreferencesRepository
from app.modules.recommender.repository.recommendations import RecommendationsRepository
from app.modules.recommender.repository.processed_events import ProcessedEventsRepository

# obtener categorias y preferencias de user de valkey

class RecommenderService:
    def __init__(self, event: KafkaEvent):   
        
        client = redis.Redis(
            host="valkey", # redis permite conectarnos con Valkey. Aqui va el host_name, en esta caso, va el nombre del servicio en el compose
            port=6379, # puerto en el que corre Valkey
            decode_responses=True # Decodifica de bytes a str
        )

        self.event = event
        self.recommendation_repository = RecommendationsRepository(client=client)
        self.preferences_repository = PreferencesRepository(client=client)
        self.processed_events_repository = ProcessedEventsRepository(client=client)


    def generate_recommendation(self):
        event_id = self.event.event_id

        # 0. verificamos si evento ya fue procesado o no con su event_id
        exists = self.processed_events_repository.is_processed(event_id=event_id)

        if exists:
            return

        user_id = self.event.user_id
        # 1. Aplicar reglas para puntos de afinidad y actualizar preferencias del user
        self.event_analysis()

        # 2. Obtener top 3 categorias más afines al usuario
        recommendations = self.preferences_repository.get_highests_affinity(user_id=user_id)

        # 3. guardar recomendacion -> RecommendationsRepository guarda el resultado en Valkey para que endpoint de backend lo pueda buscar
        self.recommendation_repository.set_recommendations(user_id=user_id, categories=recommendations)

        # 4. marcar evento como procesado
        self.processed_events_repository.mark_processed(event_id=event_id)


    def event_analysis(self):
        event = self.event
        match event.event_type:
            case PlaybackEventType.IN_PROGRESS:
                self.event_in_progress()

            case PlaybackEventType.ABANDONED:
                self.event_abandoned()


    # entre más tiempo quede viendo el video, más affinity tendrá con esa categoria
    def event_in_progress(self):
        event = self.event
        user_id = event.user_id
        delta_affinity = self._get_delta_affinity()   

        # con el delta calculado, lo añadimos -> progress es una recompensa, por eso se pasa positivo
        self.preferences_repository.update_affinity(user_id=user_id, category=event.category, amount=delta_affinity)

    def event_abandoned(self):
        event = self.event

        # se penaliza solo si scrolleó video, no si fue que cambio de modulo o algo (desmontar)
        if event.reason and event.reason != AbandonReason.NAVIGATION:
            return

        user_id = event.user_id
        delta_affinity = self.get_delta_afinity()   

        if event.position_seconds <= event.duration_seconds * 0.25: # si se vió menos del 25%, se resta delta_affinity
            self.preferences_repository.update_affinity(user_id=user_id, category=event.category, amount=-min(0.25, delta_affinity)) 

        # si se abandona despues del 25% no se pensaliza

    def _get_delta_affinity(self) -> float:
        delta_affinity: float

        # asi, todos los videos tendrán recompensa máxima de 1
        if self.event.milestone_percent: # no nos importa el valor, cada que llegue, se le suma delta, si llegan 4 (o sea, 100%) afinidad será de 1
                delta_affinity = 0.25
        else: 
            delta_affinity = 7 / self.event.duration_seconds # 7 porque es cada 7 seg que se envia event de un video largo (sin milestone)
        
        return delta_affinity


# TODO: Manejar reenvios de mismo event -> en valkey tener event_pocesed con sus ids? -- YA
# 2. pasar datos desde front
# configurar compose para valkey -- YA