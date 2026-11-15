import { useEffect, useState } from "react";
import { getVideos } from "../api/videosApi";
import type { Video } from "../types";
import { VideoCard } from "./VideoCard";
import styles from "./VideoFeed.module.css";

type FeedState =
    | { status: "loading" }
    | { status: "error"; message: string }
    | { status: "ready"; videos: Video[] };

export function VideoFeed() {
    const [state, setState] = useState<FeedState>({ status: "loading" });

    useEffect(() => {
        let cancelled = false;

        getVideos()
            .then((response) => {
                if (!cancelled) {
                    setState({ status: "ready", videos: response.items });
                }
            })
            .catch((error: unknown) => {
                if (!cancelled) {
                    const message =
                        error instanceof Error
                            ? error.message
                            : "No se pudieron cargar los videos.";
                    setState({ status: "error", message });
                }
            });

        return () => {
            cancelled = true;
        };
    }, []);

    if (state.status === "loading") {
        return <p className={styles.message}>Cargando videos…</p>;
    }

    if (state.status === "error") {
        return <p className={styles.message}>{state.message}</p>;
    }

    if (state.videos.length === 0) {
        return <p className={styles.message}>Todavía no hay videos.</p>;
    }

    return (
        <div className={styles.feed}>
            {state.videos.map((video) => (
                <VideoCard key={video.id} video={video} />
            ))}
        </div>
    );
}
