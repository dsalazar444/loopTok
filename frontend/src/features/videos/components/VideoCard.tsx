import type { Video } from "../types";
import { VideoPlayer } from "./VideoPlayer";
import { LikeButton } from "../../interactions/components/LikeButton";
import { NotInterestedMenu } from "../../interactions/components/NotInterestedMenu";

import styles from "./styles/VideoCard.module.css";

interface VideoCardProps {
    video: Video;
    isActive: boolean;
    onLike: () => void;
    isLikePending: boolean;
    onNotInterested: () => void;
}

export function VideoCard({
    video,
    isActive,
    onLike,
    isLikePending,
    onNotInterested,
}: VideoCardProps) {
    return (
        <article className={styles.card}>
            <div className={styles.media}>
                <VideoPlayer
                    url={video.url}
                    category={video.category}
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

                    <NotInterestedMenu onSelect={onNotInterested} />
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