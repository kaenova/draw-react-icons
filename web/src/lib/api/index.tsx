import axios from 'axios';

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_PYTHON_API,
  withCredentials: true
});

export default api;
