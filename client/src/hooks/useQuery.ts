import { useState, useCallback, useEffect } from 'react';

interface APIProps<Data> {
  onSuccess?: (data: Data) => void;
  onError?: (error: unknown) => void;
  onSettled?: (error: unknown | null, data: Data | null) => void; // Update function signature
  queryFn: () => Promise<Data>;
}

function useQuery<Data>({ onSuccess, onError, onSettled, queryFn }: APIProps<Data>) {
  const [data, setData] = useState<Data | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<unknown>(null);

  const trigger = useCallback(async () => {
    setError(null);
    setIsLoading(true);
    let results: Data | null = null;
    let _error: unknown | null = null;
    try {
      results = await queryFn();
      setData(results);
      if (onSuccess) onSuccess(results);
    } catch (e) {
      if (onError) onError(e);
      _error = e;
      setError(e);
    } finally {
      setIsLoading(false);
      if (onSettled) onSettled(_error, results);
    }
  }, [onError, onSettled, onSuccess, queryFn]);

  useEffect(() => {
    trigger();
  }, [trigger]);

  return { data, isLoading, error, isError: Boolean(error), trigger };
}

export default useQuery;
