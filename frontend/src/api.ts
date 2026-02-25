import axios, { AxiosInstance } from 'axios';

export interface ChatRequest {
  question: string;
}

export interface ChatResponse {
  answer: string;
  generated_sql: string;
  data_preview: Record<string, unknown>[];
}

class APIClient {
  private client: AxiosInstance;

  constructor(baseURL: string = '/api') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });
  }

  async askQuestion(question: string): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>('/chat', {
      question,
    });
    return response.data;
  }

  async checkHealth(): Promise<{ status: string; service: string; environment: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const apiClient = new APIClient();
