export function getYouTubeVideoId(url: string): string | null {
    try {
        const parsed = new URL(url);
        if (!['youtube.com', 'www.youtube.com', 'm.youtube.com'].includes(parsed.hostname)) {
            return null;
        }
        if (parsed.pathname !== '/watch') return null;
        const id = parsed.searchParams.get('v');
        return id && /^[a-zA-Z0-9_-]{11}$/.test(id) ? id : null;
    } catch {
        return null;
    }
}
