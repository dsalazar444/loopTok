import type { Video } from "../types";
import styles from "./VideoCard.module.css";

export function VideoCard({ video }: { video: Video }) {
    return (
        <article className={styles.card}>
            <div className={styles.media}>
                {/* shortcut: mp4 local vía /dev-media del backend, reemplazar por la URL de GET /videos/{id}/playback */}
                <video
                    className={styles.video}
                    src={`${import.meta.env.VITE_API_BASE_URL}/dev-media/${video.id}.mp4`}
                    autoPlay
                    muted
                    loop
                    playsInline
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
