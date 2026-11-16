
import { useEffect, useRef, useState } from "react";

import { useAuth } from "../../auth/context/AuthContext";
import { usePlaybackTracking } from "../../events/hooks/usePlaybackTracking";
import type { PlaybackSample } from "../../events/types";
// import type { PlaybackSample } from "../../services/playbackEvent";


type PlayerState =
  | "loading"
  | "ready"
  | "playing"
  | "paused"
  | "error";

interface YouTubePlayer {
  playVideo(): void;
  pauseVideo(): void;
  mute(): void;
  unMute(): void;
  isMuted(): boolean;
  getCurrentTime(): number;
  getDuration(): number;
  seekTo(seconds: number, allowSeekAhead: boolean): void;
  destroy(): void;
}

interface YouTubeNamespace {
  Player: new (
    element: HTMLElement,
    options: {
      videoId: string;
      playerVars: Record<string, string | number>;
      events: {
        onReady: (event: { target: YouTubePlayer }) => void;
        onStateChange: (event: { data: number }) => void;
        onError: (event: { data: number }) => void;
        onAutoplayBlocked?: () => void;
      };
    }
  ) => YouTubePlayer;
}

declare global {
  interface Window {
    YT?: YouTubeNamespace;
    onYouTubeIframeAPIReady?: () => void;
  }
}

const YOUTUBE_STATE = {
  ENDED: 0,
  PLAYING: 1,
  PAUSED: 2,
  BUFFERING: 3,
} as const;

let apiPromise: Promise<YouTubeNamespace> | null = null;

function loadYouTubeAPI(): Promise<YouTubeNamespace> {
  if (window.YT?.Player) {
    return Promise.resolve(window.YT);
  }

  if (apiPromise) return apiPromise;

  apiPromise = new Promise<YouTubeNamespace>((resolve, reject) => {
    const previousCallback = window.onYouTubeIframeAPIReady;

    window.onYouTubeIframeAPIReady = () => {
      previousCallback?.();

      if (window.YT?.Player) {
        resolve(window.YT);
      } else {
        reject(new Error("YouTube API unavailable"));
      }
    };

    const script = document.createElement("script");
    script.src = "https://www.youtube.com/iframe_api";
    script.async = true;

    script.onerror = () => {
      reject(new Error("Could not load YouTube API"));
    };

    document.head.appendChild(script);
  }).catch((error: unknown) => {
    apiPromise = null;
    throw error;
  });

  return apiPromise;
}

// Read the latest playback position and duration.
function getPlaybackSample(
  player: YouTubePlayer
): PlaybackSample {
  return {
    positionSeconds: player.getCurrentTime(),
    durationSeconds: player.getDuration(),
  };
}

export function useYouTubePlayer(
  videoId: string | null,
  isActive: boolean
) {
  const { isAuthenticated } = useAuth();

  const tracking = usePlaybackTracking(
    videoId,
    isAuthenticated
  );

  const containerRef = useRef<HTMLDivElement>(null);
  const playerRef = useRef<YouTubePlayer | null>(null);

  const activeRef = useRef(isActive);
  const authenticatedRef = useRef(isAuthenticated);
  const trackingRef = useRef(tracking);

  const isPlayerReadyRef = useRef(false);
  const hasCompletedRef = useRef(false);

  const [state, setState] = useState<PlayerState>("loading");
  const [muted, setMuted] = useState(true);
  const [progress, setProgress] = useState(0);

  // Keep event callbacks synchronized with current React values.
  activeRef.current = isActive;
  authenticatedRef.current = isAuthenticated;
  trackingRef.current = tracking;

  // Handle final component unmount.
  useEffect(() => {
    return () => {
      const player = playerRef.current;

      if (player && isPlayerReadyRef.current) {
        trackingRef.current.abandon(
          getPlaybackSample(player),
          "unmount"
        );
      } else {
        trackingRef.current.discard();
      }
    };
  }, []);

  // Start or stop playback when the active feed video changes.
  useEffect(() => {
    const player = playerRef.current;

    if (!player || !isPlayerReadyRef.current) return;

    if (isActive) {
      player.playVideo();
    } else {
      trackingRef.current.abandon(
        getPlaybackSample(player),
        "navigation"
      );

      player.pauseVideo();
    }
  }, [isActive]);

  // Stop tracking if the authentication session expires.
  useEffect(() => {
    const player = playerRef.current;

    if (!isAuthenticated) {
      trackingRef.current.discard();
      return;
    }

    if (
      isActive &&
      state === "playing" &&
      player &&
      isPlayerReadyRef.current
    ) {
      trackingRef.current.start(
        getPlaybackSample(player)
      );
    }
  }, [isAuthenticated, isActive, state]);

  // Create the YouTube player.
  useEffect(() => {
    if (!videoId || !containerRef.current) {
      setState("error");
      return;
    }

    let disposed = false;
    let createdPlayer: YouTubePlayer | null = null;

    setState("loading");
    setMuted(true);
    setProgress(0);

    hasCompletedRef.current = false;

    const mount = document.createElement("div");
    containerRef.current.appendChild(mount);

    void loadYouTubeAPI()
      .then((YT) => {
        if (disposed) return;

        createdPlayer = new YT.Player(mount, {
          videoId,
          playerVars: {
            autoplay: 0,
            controls: 0,
            playsinline: 1,
            rel: 0,
          },
          events: {
            onReady: ({ target }) => {
              if (disposed) return;

              playerRef.current = target;
              isPlayerReadyRef.current = true;

              target.mute();

              setMuted(true);
              setState("ready");

              if (activeRef.current) {
                target.playVideo();
              }
            },

            onStateChange: ({ data }) => {
              if (disposed) return;

              const player = playerRef.current;

              if (!player || !isPlayerReadyRef.current) {
                return;
              }

              const sample = getPlaybackSample(player);

              switch (data) {
                case YOUTUBE_STATE.PLAYING:
                  if (!activeRef.current) {
                    player.pauseVideo();
                    return;
                  }

                  hasCompletedRef.current = false;

                  trackingRef.current.start(sample);
                  setState("playing");
                  break;

                case YOUTUBE_STATE.PAUSED:
                  trackingRef.current.pause(sample);
                  setState("paused");
                  break;

                case YOUTUBE_STATE.BUFFERING:
                  trackingRef.current.pause(sample);
                  setState("loading");
                  break;

                case YOUTUBE_STATE.ENDED:
                  if (hasCompletedRef.current) return;

                  hasCompletedRef.current = true;

                  trackingRef.current.complete(sample);
                  setProgress(100);
                  setState("paused");

                  // Restart automatically while preserving the tracker.
                  if (activeRef.current) {
                    player.seekTo(0, true);
                    player.playVideo();
                  }

                  break;
              }
            },

            onError: () => {
              if (disposed) return;

              const player = playerRef.current;

              if (player) {
                trackingRef.current.pause(
                  getPlaybackSample(player)
                );
              }

              setState("error");
            },

            onAutoplayBlocked: () => {
              if (disposed) return;

              const player = playerRef.current;

              if (player) {
                trackingRef.current.pause(
                  getPlaybackSample(player)
                );
              }

              setState("paused");
            },
          },
        });
      })
      .catch(() => {
        if (!disposed) setState("error");
      });

    return () => {
      disposed = true;

      if (createdPlayer) {
        trackingRef.current.abandon(
          getPlaybackSample(createdPlayer),
          "unmount"
        );

        createdPlayer.destroy();
      } else {
        trackingRef.current.discard();
      }

      isPlayerReadyRef.current = false;
      playerRef.current = null;

      mount.remove();
    };
  }, [videoId]);

  // Update the progress bar and playback metrics.
  useEffect(() => {
    if (state !== "playing") return;

    const timer = window.setInterval(() => {
      const player = playerRef.current;

      if (
        !player ||
        !isPlayerReadyRef.current ||
        !activeRef.current
      ) {
        return;
      }

      const sample = getPlaybackSample(player);

      const { positionSeconds, durationSeconds } = sample;

      setProgress(
        durationSeconds > 0
          ? (positionSeconds / durationSeconds) * 100
          : 0
      );

      if (authenticatedRef.current) {
        trackingRef.current.progress(sample);
      }
    }, 250);

    return () => window.clearInterval(timer);
  }, [state]);

  function togglePlayback() {
    const player = playerRef.current;

    if (
      !isActive ||
      !isPlayerReadyRef.current ||
      !player
    ) {
      return;
    }

    if (state === "playing") {
      player.pauseVideo();
    } else {
      player.playVideo();
    }
  }

  function toggleMute() {
    const player = playerRef.current;

    if (!isPlayerReadyRef.current || !player) return;

    if (player.isMuted()) {
      player.unMute();
    } else {
      player.mute();
    }

    setMuted(player.isMuted());
  }

  function seek(percent: number) {
    const player = playerRef.current;

    if (!isPlayerReadyRef.current || !player) return;

    const duration = player.getDuration();

    const clampedPercent = Math.max(
      0,
      Math.min(percent, 100)
    );

    if (duration > 0) {
      player.seekTo(
        (clampedPercent / 100) * duration,
        true
      );
    }

    setProgress(clampedPercent);
  }

  return {
    containerRef,
    state,
    muted,
    progress,
    togglePlayback,
    toggleMute,
    seek,
  };
}
