import type { Video } from "../types";
import { VideoPlayer } from "./VideoPlayer";
import { LikeButton } from "../../interactions/components/LikeButton";

import styles from "./styles/VideoCard.module.css";

interface VideoCardProps {
    video: Video;
    isActive: boolean;
    onLike: () => void;
    isLikePending: boolean;
}

export function VideoCard({
    video,
    isActive,
    onLike,
    isLikePending,
}: VideoCardProps) {
    return (
        <article className={styles.card}>
            <div className={styles.media}>
                <VideoPlayer
                    url={video.url}
                    isActive={isActive}
                    title={video.title}
                />

                <div className={styles.actions}>
                    <LikeButton
                        isLiked={video.isLiked}
                        likesCount={video.likesCount}
                        isPending={isLikePending}
                        onClick={onLike}
                    />
                </div>

                <div className={styles.overlay}>
                    <h2 className={styles.title}>
                        {video.title}
                    </h2>

                    <p className={styles.description}>
                        {video.description ?? "Sin descripción"}
                    </p>

                    {video.category && (
                        <span className={styles.badge}>
                            {video.category}
                        </span>
                    )}
                </div>
            </div>
        </article>
    );
}