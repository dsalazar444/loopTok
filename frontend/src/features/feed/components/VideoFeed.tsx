import { useEffect, useRef, useState } from "react";
import { getVideos } from "../../videos/api/videosApi";
import type { Video } from "../../videos/types";
import { VideoCard } from "../../videos/components/VideoCard";
import styles from "./styles/VideoFeed.module.css";

type FeedState =
    | { status: "loading" }
    | { status: "error"; message: string }
    | { status: "ready"; videos: Video[] };

export function VideoFeed() {
    const [state, setState] = useState<FeedState>({
        status: "loading",
    });

    const [activeVideoId, setActiveVideoId] = useState<string | null>(
        null
    );

    const feedRef = useRef<HTMLDivElement>(null);

    // Fetch video metadata
    useEffect(() => {
        let cancelled = false;

        getVideos()
            .then((response) => {
                if (!cancelled) {
                    setState({
                        status: "ready",
                        videos: response.items,
                    });
                }
            })
            .catch((error: unknown) => {
                if (!cancelled) {
                    const message =
                        error instanceof Error
                            ? error.message
                            : "No se pudieron cargar los videos.";

                    setState({
                        status: "error",
                        message,
                    });
                }
            });

        return () => {
            cancelled = true;
        };
    }, []);

    // Track which video is visible
    useEffect(() => {
        if (state.status !== "ready") return;

        const container = feedRef.current;
        if (!container) return;

        const visibility = new Map<Element, number>();

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    visibility.set(
                        entry.target,
                        entry.isIntersecting
                            ? entry.intersectionRatio
                            : 0
                    );
                });

                let mostVisible: Element | null = null;
                let highestRatio = 0.5;

                visibility.forEach((ratio, element) => {
                    if (ratio > highestRatio) {
                        highestRatio = ratio;
                        mostVisible = element;
                    }
                });

                const videoId = mostVisible
                    ? (mostVisible as HTMLElement).dataset.videoId
                    : null;

                setActiveVideoId(videoId ?? null);
            },
            {
                root: null,
                threshold: [0, 0.25, 0.5, 0.75, 1],
            }
        );

        const cards = container.querySelectorAll(
            "[data-video-id]"
        );

        cards.forEach((card) => {
            visibility.set(card, 0);
            observer.observe(card);
        });

        return () => {
            observer.disconnect();
        };
    }, [state]);

    if (state.status === "loading") {
        return (
            <div
                className={styles.loading}
                role="status"
                aria-label="Cargando videos"
            >
                <div className={styles.spinner} />
            </div>
        );
    }

    if (state.status === "error") {
        return (
            <p className={styles.message}>
                {state.message}
            </p>
        );
    }

    if (state.videos.length === 0) {
        return (
            <p className={styles.message}>
                Todavía no hay videos.
            </p>
        );
    }

    return (
        <div className={styles.feed} ref={feedRef}>
            {state.videos.map((video) => (
                <div
                    key={video.id}
                    className={styles.item}
                    data-video-id={video.id}
                >
                    <VideoCard
                        video={video}
                        isActive={activeVideoId === video.id}
                    />
                </div>
            ))}
        </div>
    );
}
