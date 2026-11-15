import { httpRequest } from "../../../lib/http/httpClient";
import type { VideoListResponse } from "../../videos/types";

export function getVideos(): Promise<VideoListResponse> {
    return httpRequest<VideoListResponse>("/videos");
}
