import axios from 'axios';
import { useCallback } from 'react';

import useQuery from '../../hooks/useQuery.ts';
import { getBaseURL } from '../../common/url.ts';

async function getFacesGallery(faceName: string) {
  const response = await axios.get(`${getBaseURL()}/faces/${faceName}/gallery`);
  return response.data;
}

function useGetFacesGallery(faceName: string, onSuccess: (data: string[]) => void) {
  const _getFacesGallery = useCallback(() => getFacesGallery(faceName), [faceName]);

  return useQuery({
    queryFn: _getFacesGallery,
    onSuccess
  });
}

export default useGetFacesGallery;
