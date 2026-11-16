from uuid import UUID
import json
from app.modules.events.schemas import EventRequest

class PlaybackService:
    def publish_playback_event(self, user_id: UUID, event: EventRequest):
        # convertimos objeto en un json
        event_data = event.model_dump(mode="json",by_alias=True, exclude=None) 
        # by_alias= true es para que cuando lo convierta a json, mantenga las claves con el alias que se define en el esquema (camelCase) para mantener consistencia con el front
        # exclude=None para que no añada parametros que tengan valor none
        
        # añadimos key de user id
        event_data["userId"] = str(user_id)
        # Para que agente identifique y capture solo estos logs, no los de erores, ni nada.
        event_data["logType"] = "playback_event"

        # convertimos a string para mandarla por stdout
        json_string = json.dumps(event_data)

        print(json_string, flush=True) # mandamos por stdout para que agente lo obtenga