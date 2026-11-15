import { getYouTubeVideoId } from '../utils/youtube';
import { useYouTubePlayer } from '../hooks/useYouTubePlayer';
import styles from '../styles/VideoPlayer.module.css';

interface VideoPlayerProps {
    url: string;
    isActive: boolean;
    title?: string;
}

export function VideoPlayer({ url, isActive, title = 'YouTube video' }: VideoPlayerProps) {
    const videoId = getYouTubeVideoId(url);
    const { containerRef, state, muted, progress, togglePlayback, toggleMute, seek } =
        useYouTubePlayer(videoId, isActive);

    return (
        <section className={styles.player} aria-label={title}>
            <div ref={containerRef} className={styles.youtube} />

            {state === 'loading' && <div className={styles.status} role="status">Loading video…</div>}
            {state === 'error' && (
                <div className={styles.status} role="alert">
                    This video cannot be played here.
                    {videoId && <a href={url} target="_blank" rel="noopener noreferrer">Watch on YouTube</a>}
                </div>
            )}

            {state !== 'error' && (
                <div className={styles.controls}>
                    <button type="button" onClick={togglePlayback} disabled={!isActive || state === 'loading'}
                        aria-label={state === 'playing' ? 'Pause video' : 'Play video'}>
                        {state === 'playing' ? 'Ⅱ' : '▶'}
                    </button>
                    <button type="button" onClick={toggleMute} disabled={state === 'loading'}
                        aria-label={muted ? 'Unmute video' : 'Mute video'}>
                        {muted ? 'Muted' : 'Sound on'}
                    </button>
                    <input type="range" min="0" max="100" step="0.1" value={progress}
                        onChange={(event) => seek(Number(event.target.value))}
                        aria-label="Video progress" disabled={state === 'loading'} />
                </div>
            )}
        </section>
    );
}
