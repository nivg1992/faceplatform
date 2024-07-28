import axios from 'axios';

import { getBaseURL } from '../../common/url';
import useMutation from '../../hooks/useMutation.ts';

async function deleteFaceImg({ faceName, imageId }: { faceName: string; imageId: string }): Promise<void> {
  await axios.delete(`${getBaseURL()}/faces/${faceName}/${imageId}`);
}

function useDeleteFaceImage(onSuccess: () => void) {
  return useMutation({
    onSuccess,
    mutationFn: deleteFaceImg
  });
}
export default useDeleteFaceImage;
