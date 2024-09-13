import axios from 'axios';

import { getBaseURL } from '../../common/url.ts';
import useMutation from '../../hooks/useMutation.ts';

function deleteFace(name: string) {
  return axios.delete(`${getBaseURL()}/faces/${name}`);
}

function useFaceDelete(onSuccess: () => void) {
  return useMutation({
    mutationFn: deleteFace,
    onSuccess
  });
}

export default useFaceDelete;
