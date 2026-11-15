export interface Video {
  id: string;
  title: string;
  description: string;
  category: string;
  subcategory: string | null;
  url: string;
  likesCount: number;
  isLiked: boolean;
}

export interface VideoListResponse {
  items: Video[];
  total: number;
  page: number;
  pageSize: number;
}
