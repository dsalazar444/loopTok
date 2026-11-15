import type { Video } from "../types";
import { VideoPlayer } from "./VideoPlayer";
import styles from "./styles/VideoCard.module.css";

interface VideoCardProps {
    video: Video;
    isActive: boolean;
}

export function VideoCard({ video, isActive }: VideoCardProps) {
    return (
        <article className={styles.card}>
            <div className={styles.media}>
                <VideoPlayer
                    url={video.url}
                    isActive={isActive}
                    title={video.title}
                />

                <div className={styles.overlay}>
                    <h2 className={styles.title}>{video.title}</h2>
                    <p className={styles.description}>{video.description}</p>
                    {video.category && (
                        <span className={styles.badge}>{video.category}</span>
                    )}
                </div>
            </div>
        </article>
    );
}

