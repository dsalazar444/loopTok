export interface Video {
  id: string;
  title: string;
  description: string;
  category: string;
  subcategory: string | null;
}

export interface VideoListResponse {
  items: Video[];
  total: number;
  page: number;
  pageSize: number;
}
