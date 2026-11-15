import { apiRequest } from "../../../shared/api/httpClient";
import type { VideoListResponse } from "../types";

export function getVideos(token?: string | null): Promise<VideoListResponse> {
    return apiRequest<VideoListResponse>("/videos", {
        token: token ?? undefined,
    });
}