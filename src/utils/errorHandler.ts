import { AxiosError } from 'axios';

export const handleApiError = (error: AxiosError) => {
  if (error.code === 'ERR_NETWORK') {
    return {
      error: true,
      message: 'Network connection error. Please check your internet connection.',
      status: 'network_error'
    };
  }

  return {
    error: true,
    message: error.message || 'An unexpected error occurred',
    status: error.response?.status || 'unknown'
  };
};
