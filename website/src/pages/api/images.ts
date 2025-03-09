import type { NextApiRequest, NextApiResponse } from "next";
import { ImageListResponse } from "@/types/content";

export interface ImageQueryParams {
  page?: number;
  per_page?: number;
  tags?: string;
  from_date?: string;
  to_date?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ImageListResponse>
) {
  // Extract and validate query parameters
  const {
    page = 1,
    per_page = 20,
    tags,
    from_date,
    to_date,
    sort_by = 'created_at',
    sort_order = 'desc'
  } = req.query;

  // Build query string
  const queryParams = new URLSearchParams({
    page: String(page),
    per_page: String(per_page)
  });

  if (tags) queryParams.append('tags', String(tags));
  if (from_date) queryParams.append('from_date', String(from_date));
  if (to_date) queryParams.append('to_date', String(to_date));
  if (sort_by) queryParams.append('sort_by', String(sort_by));
  if (sort_order) queryParams.append('sort_order', String(sort_order));
  
  try {
    const response = await fetch(
      `http://127.0.0.1:8887/api/content/images/list?${queryParams.toString()}`
    );
    
    if (!response.ok) {
      const errorText = await response.text();
      if (process.env.NODE_ENV === 'development') {
        console.error('API Error:', {
          status: response.status,
          statusText: response.statusText,
          body: errorText
        });
      }
      throw new Error('Failed to fetch images');
    }

    const data: ImageListResponse = await response.json();
    res.status(200).json(data);
  } catch (error) {
    if (process.env.NODE_ENV === 'development') {
      console.error('API Handler Error:', error);
    }
    res.status(500).json({
      items: [],
      page: Number(page),
      pages: 0,
      per_page: Number(per_page),
      total: 0
    });
  }
} 