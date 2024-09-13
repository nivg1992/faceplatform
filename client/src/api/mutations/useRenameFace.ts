import axios from 'axios';

import { getBaseURL } from '../../common/url';
import useMutation from '../../hooks/useMutation.ts';

interface RenameFaceParams {
  source_face: string;
  dest_face: string;
}

interface RenameResponse {
  action: string;
}

async function renameFace({ source_face, dest_face }: RenameFaceParams): Promise<RenameResponse> {
  const response = await axios.post(`${getBaseURL()}/faces/rename`, {
    source_face,
    dest_face
  });
  return response.data;
}

function useRenameFace(onSuccess: (data: RenameResponse) => void) {
  return useMutation({
    onSuccess,
    mutationFn: renameFace
  });
}

export default useRenameFace;
