import { useState, useCallback, useEffect } from 'react';

interface APIProps<Data> {
  onSuccess?: (data: Data) => void;
  onError?: (error: unknown) => void;
  onSettled?: () => void;
  queryFn: () => Promise<Data>;
}

function useQuery<Data>({ onSuccess, onError, onSettled, queryFn }: APIProps<Data>) {
  const [data, setData] = useState<Data | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const trigger = useCallback(async () => {
    setIsLoading(true);
    try {
      const results = await queryFn();
      setData(results);
      if (onSuccess) onSuccess(results);
    } catch (error) {
      if (onError) onError(error);
    } finally {
      setIsLoading(false);
      if (onSettled) onSettled();
    }
  }, [onError, onSettled, onSuccess, queryFn]);

  useEffect(() => {
    trigger();
  }, [trigger]);

  return { data, isLoading, trigger };
}

export default useQuery;
