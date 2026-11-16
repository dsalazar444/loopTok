import { apiRequest } from "../../../shared/api/httpClient";
import type { PlaybackEvent } from "../types"

export function sendPlaybackEvent(token: string, event: PlaybackEvent): Promise<void> {
    return apiRequest<void>("/events/reproduction", {
        method: "POST",
        token,
        body: JSON.stringify(event),
    });
}