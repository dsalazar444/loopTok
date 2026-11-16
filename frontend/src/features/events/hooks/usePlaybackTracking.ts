// 	Administrar el ciclo de vida del tracker y reaccionar a inicio, pausa, finalización y abandono.
// administrar la instancia de PlaybackTracker
import { useCallback, useRef } from "react";

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

  // Temporary event handler for testing. -> implementacion de handles especificaod en types
  const handleEvent = useCallback((event: PlaybackEvent) => {
    console.log("[LoopTok Playback]", event); // despues, ddeberá usar api para comunicarse con back
  }, []);

  // Create a tracker only when playback actually starts.
  const start = useCallback(
    (sample: PlaybackSample) => {
      if (!isAuthenticated || !videoId) return; // si no esta auth o no hay video, no se crea tracker
    // creamos tracker si no existe
      if (!trackerRef.current) {
        trackerRef.current = new PlaybackTracker(
          videoId,
          handleEvent
        );
      }

      trackerRef.current.start(sample);
    },
    [videoId, isAuthenticated, handleEvent]
  );

  // Update playback metrics periodically.
  const progress = useCallback(
    (sample: PlaybackSample) => {
      trackerRef.current?.progress(sample);
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

  // Complete the current loop without discarding the tracker.
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
      trackerRef.current = null;
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
