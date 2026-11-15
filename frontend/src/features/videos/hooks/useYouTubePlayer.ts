// comunicación con la API de YouTube
import { useEffect, useRef, useState } from 'react';

type PlayerState = 'loading' | 'ready' | 'playing' | 'paused' | 'error';

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
    Player: new (element: HTMLElement, options: {
        videoId: string;
        playerVars: Record<string, string | number>;
        events: {
            onReady: (event: { target: YouTubePlayer }) => void;
            onStateChange: (event: { data: number }) => void;
            onError: (event: { data: number }) => void;
            onAutoplayBlocked?: () => void;
        };
    }) => YouTubePlayer;
}

declare global {
    interface Window {
        YT?: YouTubeNamespace;
        onYouTubeIframeAPIReady?: () => void;
    }
}

let apiPromise: Promise<YouTubeNamespace> | null = null;

function loadYouTubeAPI(): Promise<YouTubeNamespace> {
    if (window.YT?.Player) return Promise.resolve(window.YT);
    if (apiPromise) return apiPromise;

    apiPromise = new Promise<YouTubeNamespace>((resolve, reject) => {
        const previousCallback = window.onYouTubeIframeAPIReady;
        window.onYouTubeIframeAPIReady = () => {
            previousCallback?.();
            if (window.YT?.Player) resolve(window.YT);
            else reject(new Error('YouTube API unavailable'));
        };
        const script = document.createElement('script');
        script.src = 'https://www.youtube.com/iframe_api';
        script.async = true;
        script.onerror = () => reject(new Error('Could not load YouTube API'));
        document.head.appendChild(script);
    }).catch((error: unknown) => {
        apiPromise = null;
        throw error;
    });

    return apiPromise;
}

export function useYouTubePlayer(videoId: string | null, isActive: boolean) {
    const containerRef = useRef<HTMLDivElement>(null);
    const playerRef = useRef<YouTubePlayer | null>(null);
    const activeRef = useRef(isActive);
    const isPlayerReadyRef = useRef(false);

    const [state, setState] = useState<PlayerState>('loading');
    const [muted, setMuted] = useState(true);
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        activeRef.current = isActive;
        const player = playerRef.current;

        if (!isPlayerReadyRef.current || !player) {
            return;
        }
        if (isActive) {
            player.playVideo();
        } else {
            player.pauseVideo();
        }
    }, [isActive]);

    useEffect(() => {
        if (!videoId || !containerRef.current) {
            setState('error');
            return;
        }

        let disposed = false;
        let createdPlayer: YouTubePlayer | null = null;
        setState('loading');
        setMuted(true);
        setProgress(0);
        const mount = document.createElement('div');
        containerRef.current.appendChild(mount);

        void loadYouTubeAPI().then((YT) => {
            if (disposed) return;
            createdPlayer = new YT.Player(mount, {
                videoId,
                playerVars: {
                    autoplay: 0,
                    controls: 0,
                    loop: 1,
                    playlist: videoId,
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
                        setState('ready');

                        if (activeRef.current) {
                            target.playVideo();
                        }
                    },
                    onStateChange: ({ data }) => {
                        if (disposed) return;
                        if (data === 1) setState('playing');
                        else if (data === 2) setState('paused');
                        else if (data === 3) setState('loading');
                        else if (data === 0) setState('paused');
                    },
                    onError: () => { if (!disposed) setState('error'); },
                    onAutoplayBlocked: () => { if (!disposed) setState('paused'); },
                },
            });
        }).catch(() => { if (!disposed) setState('error'); });

        return () => {
            disposed = true;
            isPlayerReadyRef.current = false;

            playerRef.current = null;

            if (
                createdPlayer &&
                typeof createdPlayer.destroy === "function"
            ) {
                createdPlayer.destroy();
            }

            mount.remove();
        };
    }, [videoId]);

    useEffect(() => {
        if (state !== 'playing') return;
        
        const timer = window.setInterval(() => {
            const player = playerRef.current;

            if (!isPlayerReadyRef.current || !player) return;
            const duration = player.getDuration();
            setProgress(duration > 0 ? (player.getCurrentTime() / duration) * 100 : 0);
        }, 250);
        return () => window.clearInterval(timer);
    }, [state]);

    function togglePlayback() {
        const player = playerRef.current;

        if (!isActive || !isPlayerReadyRef.current || !player) {
            return;
        }

        if (state === 'playing') {
            player.pauseVideo();
        } else {
            player.playVideo();
        }
    }

    function toggleMute() {
        const player = playerRef.current;
        if (!isPlayerReadyRef.current || !player) return;
        if (player.isMuted()) player.unMute();
        else player.mute();
        setMuted(player.isMuted());
    }

    function seek(percent: number) {
        const player = playerRef.current;
        if (!isPlayerReadyRef.current || !player) return;

        const duration = player.getDuration();
        if (duration > 0) player.seekTo((Math.max(0, Math.min(percent, 100)) / 100) * duration, true);
        setProgress(percent);
    }

    return { containerRef, state, muted, progress, togglePlayback, toggleMute, seek };
}
