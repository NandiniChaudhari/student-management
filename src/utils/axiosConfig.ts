import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:5000',
  timeout: 5000,
});

axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ERR_NETWORK') {
      console.error('Network error occurred:', error.message);
      // You can dispatch to your state management system here if needed
      return Promise.reject({
        message: 'Unable to connect to the server. Please check your internet connection.',
        originalError: error,
      });
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
