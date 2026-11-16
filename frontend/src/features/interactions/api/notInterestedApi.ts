import { apiRequest } from "../../../shared/api/httpClient";

export function markNotInterested(
    videoId: string,
    token: string,
): Promise<void> {
    return apiRequest<void>(`/videos/${videoId}/not-interested`, {
        method: "POST",
        token,
    });
}
