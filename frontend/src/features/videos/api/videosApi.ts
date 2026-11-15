import { apiRequest } from "../../../shared/api/httpClient";
import type { VideoListResponse } from "../types";

export function getVideos(): Promise<VideoListResponse> {
    return apiRequest<VideoListResponse>("/videos");
}