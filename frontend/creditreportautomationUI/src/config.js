// Application configuration
const config = {
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    timeout: 30000,
  },
  server: {
    port: 3002,
    host: 'localhost',
  },
  paths: {
    analysisOutput: '/analysis_outputs',
    processedData: '/processed_data',
  },
};

export default config;
