import axios from 'axios';

import useQuery from '../../hooks/useQuery.ts';
import { getBaseURL } from '../../common/url.ts';
import { IFace } from '../../tagFaces/TagFaces.tsx';

async function getFaces() {
  const response = await axios.get(`${getBaseURL()}/faces`);
  return response.data;
}

function useGetFaces(onSuccess: (data: IFace[]) => void) {
  return useQuery({
    queryFn: getFaces,
    onSuccess
  });
}

export default useGetFaces;
