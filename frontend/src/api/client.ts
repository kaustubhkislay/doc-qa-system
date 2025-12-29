import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
});

// Types
export interface Document {
  id: string;
  title: string;
  filename: string;
  page_count: number;
  upload_date: string;
  collection?: string;
}

export interface Source {
  document_id: string;
  document_title: string;
  page_number: number;
  excerpt: string;
}

export interface QueryResponse {
  answer: string;
  sources: Source[];
}

// API Functions
export const documentsApi = {
  upload: async (file: File, title: string, collection?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    if (collection) {
      formData.append('collection', collection);
    }
    
    const response = await api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  
  list: async (): Promise<{ documents: Document[] }> => {
    const response = await api.get('/documents/');
    return response.data;
  },
  
  delete: async (id: string) => {
    const response = await api.delete(`/documents/${id}`);
    return response.data;
  },
};

export const queryApi = {
  ask: async (
    question: string, 
    documentIds?: string[]
  ): Promise<QueryResponse> => {
    const response = await api.post('/query/', {
      question,
      document_ids: documentIds?.length ? documentIds : undefined,
    });
    return response.data;
  },
};

export default api;