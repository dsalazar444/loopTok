// Encargado de calcular las métricas, no usa react es lógica independiente.
import type {
  AbandonReason,
  PlaybackEvent,
  PlaybackEventHandler,
  PlaybackEventType,
  PlaybackSample,
} from "./types";

// regla de negocio: Para videos de duración <= 60 s, se mandan metricas de progreso cada que se alcance cierto porcentaje de reproducción
// Para vieos mayores de 60 s, se manda metricas de progreso cada 12 s, porque si se usa porcentajes, se podrían mandar cada mucho tiempo
// cuando un video corto alcanza estos porcentajes podemos generar un evento de progreso.
const SHORT_VIDEO_MAX_SECONDS = 60;
const LONG_VIDEO_PROGRESS_MS = 12_000;
const SHORT_VIDEO_MILESTONES = [25, 50, 75];

// uno para cada video -> guarda valores que no cambian entre eventos
// representa seguimiento de una reproducción de un video
export class PlaybackTracker {
  private readonly playbackId = crypto.randomUUID(); // permite que backend agrupe todos los eventos de una misma instancia
  private readonly videoId: string;
  private readonly category: string;
  private readonly onEvent: PlaybackEventHandler;
  // informacion que PlaybackTracker necesita para calcular metricas
  private watchTimeMs = 0; // tiempo neto, porque tendrá en cuenta las n replayed
  private lastStartedAt: number | null = null; // Instante desde el cual se está acumulando tiempo de reproducción -> porque puede haber replay -> positionSeconds es relativo a este

  private positionSeconds = 0;
  private durationSeconds = 0;
  private maxProgressPercent = 0; // Porcentaje máximo alcanzado durante el seguimiento durante 1 o más replays

  private playCount = 0;
  private isStarted = false; // Ambos is.. porque reproducción puede estar iniciada, pero estár pausada. Por eso necesitamos ambas variables
  private isPlaying = false;

  private emittedMilestones = new Set<number>(); // Porcentajes de progreso sin repetir que ya generaron eventos.
  private lastProgressWatchTimeMs = 0; // Tiempo neto acumulado cuando se emitió el último evento de progreso de un video largo.

  constructor(videoId: string, category: string, onEvent: PlaybackEventHandler) {
    this.videoId = videoId;
    this.category = category;
    this.onEvent = onEvent; //guarda la funcion recibida para usarla posteriormente.
  }


  // sirve para contabilizar únicamente el tiempo durante el cual el video está reproduciéndose, sin incluir las pausas.
  private accumulateWatchTime(): void {
    // no actualiza si no se esta reproducionedo -> no cuenta pausas
    if (!this.isPlaying || this.lastStartedAt === null) {
      return;
    }
    // obtenemos timestamp actual
    const now = performance.now();
    //calcular cuanto tiempo pasó:
    // al tiempo neto, añadimos nuevo "bloque", que iria desde la ultima vez que se despausó hasta ahora
    // por ejemplo, empiezan a reproducir en t=1, entonces laststartedat=1, y cuando se llame esta funcion (pro ejm en progress)
    // 3 s despues, laststared=1 y tactual=3, el watchtime seria 3-1 = 2, porque es el tiempo neto
    // luego, laststared = 3 , y cuando se vuelva a llamar, se acumulará con lo que ya teniamos (+=)
    this.watchTimeMs += Math.max(
      0,
      now - this.lastStartedAt
    );

    this.lastStartedAt = now;
  }

  // se encarga de registrar nuevo evento de ese playtracker (de un video en especifico)
  private createEvent(
    eventType: PlaybackEventType,
    reason?: AbandonReason,
    milestonePercent?: number
  ): PlaybackEvent {
    return {
      eventId: crypto.randomUUID(),
      eventType,
      playbackId: this.playbackId,
      videoId: this.videoId,
      timestamp: new Date().toISOString(), //obtiene la fecha/hora actual y la convierte a String

      category: this.category,

      watchTimeMs: Math.round(this.watchTimeMs), //redondear numero al entero más cercano
      positionSeconds: this.positionSeconds,
      durationSeconds: this.durationSeconds,
      maxProgressPercent: this.maxProgressPercent,

      isReplay:
        eventType === "video_completed"
            ? this.playCount > 1 // para que sea replay, en un video_completed, playcount debe > 1 porque en 1ra vez complete, playcount es 1, pero no es un replay
            : this.playCount > 0, // para otros eventos, si basta con que sea mayor que 0 (es decir, min 1) porque cuando mande progress, por ejm, sigue siendo una reproducción

      playCount: this.playCount,

      ...(reason ? { reason } : {}), // si reason existe se agrega al objeto si no se agrega {}
      ...(milestonePercent !== undefined ? { milestonePercent } : {}),
    };
  }

  // encargado de crearEvent y pasarselo a la función onEvent, 
  private emit(
    eventType: PlaybackEventType,
    reason?: AbandonReason,
    milestonePercent?: number
  ): void {
    this.onEvent(this.createEvent(eventType, reason, milestonePercent));
  }

  // actualiza progreso actual y máximo
  private updateSample(sample: PlaybackSample): void {
    const { positionSeconds, durationSeconds } = sample; //extraer las 2 propeidades de sample

    // validamos
    if (
      !Number.isFinite(positionSeconds) ||
      !Number.isFinite(durationSeconds) ||
      durationSeconds <= 0
    ) {
      return;
    }

    // positionSeconds es mayor que 0, y el minimo entre position y duration
    // se limitam la posicion de intervalo entre 0 y la duración total
    this.positionSeconds = Math.max(
      0,
      Math.min(positionSeconds, durationSeconds)
    );

    this.durationSeconds = durationSeconds;

    const percent =
      (this.positionSeconds / durationSeconds) * 100;

    // actualiza maxprogress si alcanzamos nuevo máximo en comparación con el % anterior
    this.maxProgressPercent = Math.max(
      this.maxProgressPercent,
      Math.min(100, percent)
    );
  }

  // se llama cuando video inicia o se despausa
  start(sample: PlaybackSample): void {
    if (this.isPlaying) return;

    this.updateSample(sample); // actualiza posición

    if (!this.isStarted) { // apenas inicia reproducción, no es que estaba en pausa
      this.isStarted = true; 
      this.emit("video_started");
    }

    this.isPlaying = true;
    this.lastStartedAt = performance.now(); // setteamos momento de inicio de reproduccion
  }

  // se ejecuta periodicamente mientras video se reproduce (registra el progreso)
  progress(sample: PlaybackSample): void {
    if (!this.isPlaying) return;

    // actualiza watchtime y sample (recordemos que progress se ejecuta cada cierto tiempo, entonces debe actualizar valores, pues pueden ser diferentes)
    this.accumulateWatchTime();
    this.updateSample(sample); //actualiza la posición y duración

    // verifica si hay que generar evento, si es para video corto (porcentajes) o para largo (intervalos 12segs)
    if (this.durationSeconds <= SHORT_VIDEO_MAX_SECONDS) {
      this.checkShortVideoProgress();
    } else {
      this.checkLongVideoProgress();
    }
  }

  private checkShortVideoProgress(): void {
    for (const milestone of SHORT_VIDEO_MILESTONES) {
        // si el maximo porcentaje alcanzado es mayor a porcentaje milestone, y no se ha generado evento 
      if (
        this.maxProgressPercent >= milestone && // si el user alzanzó milestone y no se ha registrado
        !this.emittedMilestones.has(milestone)
      ) {
        this.emittedMilestones.add(milestone); // añadimos milestone y generamos evento
        this.emit("video_progress", undefined, milestone); 
      }
    }
  }

  private checkLongVideoProgress(): void {
    if (
      this.watchTimeMs - this.lastProgressWatchTimeMs >=
      LONG_VIDEO_PROGRESS_MS
    ) {
      this.lastProgressWatchTimeMs = this.watchTimeMs;
      this.emit("video_progress");
    }
  }

  // Acumular el último intervalo de reproducción.
  // Actualizar la posición.
  pause(sample: PlaybackSample): void {
    if (!this.isPlaying) return;

    // actualizamos tiempos y valores de progreso antes de pausar -> para no perder nos segundos desde la ultima llamada a progress()
    this.accumulateWatchTime();
    this.updateSample(sample);

    this.isPlaying = false;
    this.lastStartedAt = null;
    //isStarted sigue como true para reaunidar sin generar otro evento video_started
  }

  complete(sample: PlaybackSample): void {
    if (!this.isStarted) return;

    this.pause(sample); // para que actualice valores 

    this.playCount += 1; //incrementa contadores de reproducciones completas
    this.emit("video_completed");

    // "reiniciamos" los valores para poder registrar una nueva reproducción
    this.isStarted = false;
    this.emittedMilestones.clear();
    this.maxProgressPercent = 0;
    this.lastProgressWatchTimeMs = this.watchTimeMs;
  }

  abandon(
    sample: PlaybackSample, //posición y duración actual 
    reason: AbandonReason = "navigation"
  ): void {
    if (!this.isStarted) return; // no se puede abandonar si no se ha iniciado

    this.pause(sample); // acumulamos ultimo intervalo
    this.emit("video_abandoned", reason);

    this.isStarted = false;
  }
}