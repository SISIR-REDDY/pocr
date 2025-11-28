// API configuration
const getApiUrl = () => {
  // In production, use environment variable or default to relative path
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // For Vercel deployment, use relative path (same domain)
  if (import.meta.env.PROD) {
    return '';
  }
  
  // Development: use localhost
  return 'http://localhost:8000';
};

export const API_BASE_URL = getApiUrl();
export const API_EXTRACT_URL = `${API_BASE_URL}/api/extract`;
export const API_VERIFY_URL = `${API_BASE_URL}/api/verify`;

