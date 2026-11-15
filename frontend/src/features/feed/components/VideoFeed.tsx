import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getVideos } from "../../videos/api/videosApi";
import type { Video } from "../../videos/types";
import { VideoCard } from "../../videos/components/VideoCard";

import { useAuth } from "../../auth/context/AuthContext";
import { addLike, removeLike } from "../../interactions/api/likesApi";
import { ApiError } from "../../../shared/api/httpClient";

import styles from "./styles/VideoFeed.module.css";

type FeedState =
    | { status: "loading" }
    | { status: "error"; message: string }
    | { status: "ready"; videos: Video[] };

export function VideoFeed() {
    const navigate = useNavigate();

    const { token, isAuthenticated, logout } = useAuth();

    const [state, setState] = useState<FeedState>({
        status: "loading",
    });

    const [activeVideoId, setActiveVideoId] = useState<string | null>(
        null
    );

    const [pendingLikes, setPendingLikes] = useState<Set<string>>(
        () => new Set()
    );

    const [likeError, setLikeError] = useState<string | null>(null);

    const feedRef = useRef<HTMLDivElement>(null);

    // Prevent simultaneous like operations on the same video
    const pendingLikesRef = useRef<Set<string>>(new Set());

    // Fetch videos and their like states
    useEffect(() => {
        let cancelled = false;

        getVideos(token)
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
                            : "Unable to load videos.";

                    setState({
                        status: "error",
                        message,
                    });
                }
            });

        return () => {
            cancelled = true;
        };
    }, [token]);

    // Handle like and unlike actions
    const handleLike = useCallback(
        async (videoId: string) => {
            if (!isAuthenticated || !token) {
                navigate("/login");
                return;
            }

            if (pendingLikesRef.current.has(videoId)) {
                return;
            }

            if (state.status !== "ready") {
                return;
            }

            const video = state.videos.find(
                (item) => item.id === videoId
            );

            if (!video) {
                return;
            }

            const wasLiked = video.isLiked;

            pendingLikesRef.current.add(videoId);

            setPendingLikes(
                (previous) => new Set(previous).add(videoId)
            );

            setLikeError(null);

            try {
                if (wasLiked) {
                    await removeLike(videoId, token);
                } else {
                    await addLike(videoId, token);
                }

                setState((previous) => {
                    if (previous.status !== "ready") {
                        return previous;
                    }

                    return {
                        ...previous,
                        videos: previous.videos.map((item) => {
                            if (item.id !== videoId) {
                                return item;
                            }

                            return {
                                ...item,
                                isLiked: !wasLiked,
                                likesCount: Math.max(
                                    0,
                                    item.likesCount + (wasLiked ? -1 : 1)
                                ),
                            };
                        }),
                    };
                });
            } catch (error) {
                if (error instanceof ApiError && error.status === 401) {
                    logout();
                    navigate("/login");
                } else {
                    setLikeError(
                        error instanceof Error
                            ? error.message
                            : "Unable to update like."
                    );
                }
            } finally {
                pendingLikesRef.current.delete(videoId);

                setPendingLikes((previous) => {
                    const updated = new Set(previous);
                    updated.delete(videoId);
                    return updated;
                });
            }
        },
        [isAuthenticated, token, state, navigate, logout]
    );

    // Observe only changes in the loaded video list
    const videoIdsKey =
        state.status === "ready"
            ? state.videos.map((video) => video.id).join("|")
            : "";

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

        const cards = container.querySelectorAll("[data-video-id]");

        cards.forEach((card) => {
            visibility.set(card, 0);
            observer.observe(card);
        });

        return () => {
            observer.disconnect();
        };
    }, [state.status, videoIdsKey]);

    if (state.status === "loading") {
        return (
            <div
                className={styles.loading}
                role="status"
                aria-label="Loading videos"
            >
                <div className={styles.spinner} />
            </div>
        );
    }

    if (state.status === "error") {
        return <p className={styles.message}>{state.message}</p>;
    }

    if (state.videos.length === 0) {
        return <p className={styles.message}>No videos available.</p>;
    }

    return (
        <div className={styles.feed} ref={feedRef}>
            {likeError && (
                <p role="alert">{likeError}</p>
            )}

            {state.videos.map((video) => (
                <div
                    key={video.id}
                    className={styles.item}
                    data-video-id={video.id}
                >
                    <VideoCard
                        video={video}
                        isActive={activeVideoId === video.id}
                        onLike={() => handleLike(video.id)}
                        isLikePending={pendingLikes.has(video.id)}
                    />
                </div>
            ))}
        </div>
    );
}