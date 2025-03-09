import { useInfiniteQuery } from '@tanstack/react-query';
import { useEffect, useRef, useState } from 'react';
import { ImageItem, ImageListResponse } from '@/types/content';
import Image from 'next/image';
import { ImageQueryParams } from '@/pages/api/images';
import { useRouter } from 'next/router';
import '@/styles/main.css';

// Helper to convert URL params to query params
function getQueryParamsFromUrl(query: Record<string, string | string[] | undefined>): Omit<ImageQueryParams, 'page'> {
  return {
    per_page: 20,
    tags: typeof query.tags === 'string' ? query.tags : undefined,
    from_date: typeof query.from_date === 'string' ? query.from_date : undefined,
    to_date: typeof query.to_date === 'string' ? query.to_date : undefined,
    sort_by: typeof query.sort_by === 'string' ? query.sort_by : 'created_at',
    sort_order: (typeof query.sort_order === 'string' && (query.sort_order === 'asc' || query.sort_order === 'desc')) 
      ? query.sort_order 
      : 'desc'
  };
}

async function fetchImagePage(
  page: number,
  queryParams: Omit<ImageQueryParams, 'page'>
): Promise<ImageListResponse> {
  const params = new URLSearchParams();
  params.append('page', String(page));
  params.append('per_page', String(queryParams.per_page));
  if (queryParams.tags) params.append('tags', queryParams.tags);
  if (queryParams.from_date) params.append('from_date', queryParams.from_date);
  if (queryParams.to_date) params.append('to_date', queryParams.to_date);
  if (queryParams.sort_by) params.append('sort_by', queryParams.sort_by);
  if (queryParams.sort_order) params.append('sort_order', queryParams.sort_order);
  
  const response = await fetch(`/api/images?${params.toString()}`);
  if (!response.ok) {
    throw new Error('Network response was not ok');
  }
  return response.json();
}

export default function FeedPage() {
  const router = useRouter();
  const observerRef = useRef<IntersectionObserver>(null);
  const loadMoreRef = useRef<HTMLDivElement>(null);
  
  // Get query params from URL
  const currentQueryParams = getQueryParamsFromUrl(router.query);
  
  // State for pending filter changes
  const [pendingParams, setPendingParams] = useState(currentQueryParams);
  const [hasChanges, setHasChanges] = useState(false);

  // Reset pending params when URL changes
  useEffect(() => {
    setPendingParams(currentQueryParams);
    setHasChanges(false);
  }, [router.query]);

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    status,
  } = useInfiniteQuery<ImageListResponse, Error>({
    queryKey: ['images', currentQueryParams],
    queryFn: ({ pageParam }) => fetchImagePage(Number(pageParam), currentQueryParams),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      if (lastPage.page < lastPage.pages) {
        return lastPage.page + 1;
      }
      return undefined;
    },
  });

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { threshold: 0.1 }
    );

    if (loadMoreRef.current) {
      observer.observe(loadMoreRef.current);
    }

    observerRef.current = observer;

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  // Filter handling functions
  const handleTagsChange = (tags: string) => {
    setPendingParams(prev => ({ ...prev, tags: tags || undefined }));
    setHasChanges(true);
  };

  const handleDateRangeChange = (fromDate: string | undefined, toDate: string | undefined) => {
    setPendingParams(prev => ({
      ...prev,
      from_date: fromDate,
      to_date: toDate
    }));
    setHasChanges(true);
  };

  const handleSortChange = (sortBy: string, sortOrder: 'asc' | 'desc') => {
    setPendingParams(prev => ({
      ...prev,
      sort_by: sortBy,
      sort_order: sortOrder
    }));
    setHasChanges(true);
  };

  const applyFilters = () => {
    const query: Record<string, string | undefined> = {};
    if (pendingParams.tags) query.tags = pendingParams.tags;
    if (pendingParams.from_date) query.from_date = pendingParams.from_date;
    if (pendingParams.to_date) query.to_date = pendingParams.to_date;
    if (pendingParams.sort_by !== 'created_at') query.sort_by = pendingParams.sort_by;
    if (pendingParams.sort_order !== 'desc') query.sort_order = pendingParams.sort_order;

    router.push({
      query
    }, undefined, { shallow: true });
  };

  if (status === 'pending') {
    return <div className="loading">Loading...</div>;
  }

  if (status === 'error') {
    return <div className="error">Error loading images</div>;
  }

  return (
    <div className="feed-container">
      <div className="filters">
        <input
          type="text"
          placeholder="Tags (comma-separated)"
          value={pendingParams.tags || ''}
          onChange={(e) => handleTagsChange(e.target.value)}
        />
        <input
          type="date"
          value={pendingParams.from_date || ''}
          onChange={(e) => handleDateRangeChange(e.target.value, pendingParams.to_date)}
        />
        <input
          type="date"
          value={pendingParams.to_date || ''}
          onChange={(e) => handleDateRangeChange(pendingParams.from_date, e.target.value)}
        />
        <select
          value={pendingParams.sort_by}
          onChange={(e) => handleSortChange(e.target.value, pendingParams.sort_order || 'desc')}
        >
          <option value="created_at">Created At</option>
          <option value="updated_at">Updated At</option>
        </select>
        <select
          value={pendingParams.sort_order}
          onChange={(e) => handleSortChange(pendingParams.sort_by || 'created_at', e.target.value as 'asc' | 'desc')}
        >
          <option value="desc">Descending</option>
          <option value="asc">Ascending</option>
        </select>
        {hasChanges && (
          <button 
            className="apply-filters-btn"
            onClick={applyFilters}
          >
            Apply Filters
          </button>
        )}
      </div>

      <div className="image-grid">
        {data?.pages.map((page) =>
          page.items.map((image: ImageItem) => (
            <div key={image.id} className="image-card">
              <Image
                src={`https://storage.googleapis.com/${image.bucket}/${image.blob_path}`}
                alt={image.blob_path}
                fill
                className="image"
              />
            </div>
          ))
        )}
        <div ref={loadMoreRef} className="load-more">
          {isFetchingNextPage && <div>Loading more...</div>}
        </div>
      </div>
    </div>
  );
} 