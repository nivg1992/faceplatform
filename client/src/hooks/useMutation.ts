import { useState, useCallback } from 'react';

interface MutationAPIProps<Data, Variables> {
  onSuccess?: (data: Data, variables: Variables) => void;
  onError?: (error: unknown, variables: Variables) => void;
  onSettled?: (data: Data | null, e: unknown, variables: Variables) => void;
  mutationFn: (variables: Variables) => Promise<Data>;
}

function useMutation<Data, Variables>({
  onSuccess,
  onError,
  onSettled,
  mutationFn
}: MutationAPIProps<Data, Variables>) {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<unknown>(null);

  const mutate = useCallback(
    async (variables: Variables) => {
      setError(null);
      setIsLoading(true);
      let data: Data | null = null;
      let e: unknown | null = null;

      try {
        data = await mutationFn(variables);
        if (onSuccess) onSuccess(data, variables);
      } catch (err) {
        e = err;
        if (onError) onError(e, variables);
        setError(e);
      } finally {
        setIsLoading(false);
        if (onSettled) {
          onSettled(data, e, variables);
        }
      }
    },
    [mutationFn, onSuccess, onError, onSettled]
  );

  return { isLoading, mutate, error, isError: Boolean(error) };
}

export default useMutation;
