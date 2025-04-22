import axios from "axios";

// Replace with your actual backend URL
const BASE_URL = "http://localhost:9000";

export interface UploadResponse {
  message: string;
  filename: string;
}

export interface QueryRequest {
  query: string;
}

export interface QueryResponse {
  answer: string;
}

export const uploadDocument = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await axios.post<UploadResponse>(`${BASE_URL}/upload`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};

export const queryIndex = async (query: string): Promise<QueryResponse> => {
  const response = await axios.post<QueryResponse>(`${BASE_URL}/query`, {
    query,
  });

  return response.data;
};

export {};
