import axios from 'axios';

import { getBaseURL } from '../../common/url';
import useQuery from '../../hooks/useQuery';
import { IEvent } from '../../events/events';

async function getEvents() {
  const response = await axios.get(`${getBaseURL()}/events`);
  return response.data;
}

function useGetEvents(onSuccess: (data: IEvent[]) => void) {
  return useQuery({
    queryFn: getEvents,
    onSuccess
  });
}

export default useGetEvents;
