import { apiRequest } from "../../../shared/api/httpClient";

export function addLike(
    videoId: string,
    token: string,
): Promise<void> {
    return apiRequest<void>(`/videos/${videoId}/like`, {
        method: "POST",
        token,
    });
}

export function removeLike(
    videoId: string,
    token: string,
): Promise<void> {
    return apiRequest<void>(`/videos/${videoId}/like`, {
        method: "DELETE",
        token,
    });
}