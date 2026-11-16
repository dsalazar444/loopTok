// 	Administrar el ciclo de vida del tracker y reaccionar a inicio, pausa, finalización y abandono.
// administrar la instancia de PlaybackTracker (permite que un componente de react controle el seguimiento de reproducción de un video)
import { useCallback, useRef } from "react";
import { sendPlaybackEvent } from "../api/playbackApi";
import { useAuth } from "../../auth/context/AuthContext";

import { PlaybackTracker } from "../playbackService";
import type {
  AbandonReason,
  PlaybackEvent,
  PlaybackSample,
} from "../types";

export function usePlaybackTracking(
  videoId: string | null,
  isAuthenticated: boolean
) {
  const trackerRef = useRef<PlaybackTracker | null>(null);
  const { token } = useAuth();

  // Temporary event handler for testing. -> implementacion de handles especificaod en types
  const handleEvent = useCallback((event: PlaybackEvent): void  => {
    if (!token) return;

    void sendPlaybackEvent(token, event).catch((error: unknown) => {
        console.error("Failed to send playback event:", error);
        
    });
  }, [token]);

  // Create a tracker only when playback actually starts. (Registrar reproducción)
  const start = useCallback(
    (sample: PlaybackSample) => {
      if (!isAuthenticated || !videoId) return; // si no esta auth, no hay video o no hay informaciond de sample, no se crea tracker
    // creamos tracker si no existe
      if (!trackerRef.current) {
        trackerRef.current = new PlaybackTracker(
          videoId,
          handleEvent //indica qué función recibirá los eventos generados
        );
      }

      trackerRef.current.start(sample); // iniciar la reproducción / iniciar el seguimiento y generar el evento video_started cuando corresponde.
    },
    [videoId, isAuthenticated, handleEvent]
  );

  // Update playback metrics periodically.
  const progress = useCallback(
    (sample: PlaybackSample) => {
      trackerRef.current?.progress(sample); //Si existe un tracker, ejecuta su método progress y pasarle el sample
    },
    []
  );

  // Stop accumulating watch time while paused.
  const pause = useCallback(
    (sample: PlaybackSample) => {
      trackerRef.current?.pause(sample);
    },
    []
  );

  // Se quiere conservar el tracker después de completar el video.
  const complete = useCallback(
    (sample: PlaybackSample) => {
      trackerRef.current?.complete(sample);
    },
    []
  );

  // End the current visit and discard its tracker.
  const abandon = useCallback(
    (
      sample: PlaybackSample,
      reason: AbandonReason
    ) => {
      trackerRef.current?.abandon(sample, reason);
      trackerRef.current = null; // Se borra la referencia al tracker
    },
    []
  );

  // Discard tracking without generating an event. (used for JWT expiration)
  const discard = useCallback(() => {
    trackerRef.current = null;
  }, []);

  return {
    start,
    progress,
    pause,
    complete,
    abandon,
    discard,
  };
}
