import { apiRequest } from "../../../shared/api/httpClient";

export function startSession(
    sessionId: string,
    token: string,
): Promise<void> {
    return apiRequest<void>("/sessions", {
        method: "POST",
        token,
        body: JSON.stringify({ session_id: sessionId }),
    });
}

// keepalive lets the request finish even while the page is closing
export function sendHeartbeat(
    sessionId: string,
    token: string,
    keepalive = false,
): Promise<void> {
    return apiRequest<void>(`/sessions/${sessionId}/heartbeat`, {
        method: "POST",
        token,
        keepalive,
    });
}

export function endSession(
    sessionId: string,
    token: string,
    keepalive = false,
): Promise<void> {
    return apiRequest<void>(`/sessions/${sessionId}/end`, {
        method: "POST",
        token,
        keepalive,
    });
}
