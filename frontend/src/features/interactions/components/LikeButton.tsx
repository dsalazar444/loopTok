import styles from "./styles/LikeButton.module.css";

interface LikeButtonProps {
    isLiked: boolean;
    likesCount: number;
    isPending: boolean;
    onClick: () => void;
}

export function LikeButton({
    isLiked,
    likesCount,
    isPending,
    onClick,
}: LikeButtonProps) {
    return (
        <button
            type="button"
            className={styles.button}
            onClick={onClick}
            disabled={isPending}
            aria-pressed={isLiked}
            aria-label={isLiked ? "Remove like" : "Like video"}
        >
            <svg
                className={`${styles.heart} ${isLiked ? styles.liked : ""}`}
                viewBox="0 0 24 24"
                width="32"
                height="32"
                aria-hidden="true"
                fill={isLiked ? "currentColor" : "none"}
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
            >
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 0 0 0-7.78z" />
            </svg>

            <span className={styles.count}>
                {likesCount}
            </span>
        </button>
    );
}