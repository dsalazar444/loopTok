export type PlaybackEventType =
  | "video_started"
  | "video_progress"
  | "video_completed"
  | "video_abandoned";

export type AbandonReason = "navigation" | "unmount";
// navigation -> user pasó a otro video -> demuestra desinteres
// unmount -> React desmontó el componente -> El usuario salió del feed y entró a su perfil -> no necesariamnete demuetsra desinteres

//PlaybackEvent representa un evento que queremos registrar
export interface PlaybackEvent {
  eventId: string; // UUID único para deduplicación
  eventType: PlaybackEventType; // Tipo de evento
  playbackId: string; // UUID del intento de reproducción
  videoId: string; // ID del video
  timestamp: string; // Fecha/hora del evento
  // user id es obtenido de JWT por backend

  category: string; // Categoría del video mostrada al usuario

  watchTimeMs: number; // Tiempo neto acumulado de reproduccion
  positionSeconds: number; // Posición actual del reproductor
  durationSeconds: number; // Duración total
  maxProgressPercent: number; // Máximo porcentaje alcanzado

  isReplay: boolean; // Indica si corresponde a una repetición
  playCount: number; // Número de vueltas completadas

  reason?: AbandonReason;
  milestonePercent?: number; // Para indicar milestone alcanzado en ese evento generado -> para videos cortos
}
// PlaybackSample representa una muestra del estado del reproductor
export interface PlaybackSample {
  positionSeconds: number;
  durationSeconds: number;
}
// función que recibe un PlaybackEvent y no devuelve ningún resultado.
export type PlaybackEventHandler = (
  event: PlaybackEvent
) => void;