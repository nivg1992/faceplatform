import { useState, useCallback } from 'react';

interface MutationAPIProps<Data, Variables> {
  onSuccess?: (data: Data) => void;
  onError?: (error: unknown) => void;
  onSettled?: () => void;
  mutationFn: (variables: Variables) => Promise<Data>;
}

function useMutation<Data, Variables>({
  onSuccess,
  onError,
  onSettled,
  mutationFn
}: MutationAPIProps<Data, Variables>) {
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const mutate = useCallback(
    async (variables: Variables) => {
      setIsLoading(true);
      try {
        const data = await mutationFn(variables);
        if (onSuccess) onSuccess(data);
      } catch (error) {
        if (onError) onError(error);
      } finally {
        setIsLoading(false);
        if (onSettled) onSettled();
      }
    },
    [onError, onSettled, onSuccess, mutationFn]
  );

  return { isLoading, mutate };
}

export default useMutation;
