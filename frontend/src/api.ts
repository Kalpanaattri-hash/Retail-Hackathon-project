import axios, { AxiosInstance } from 'axios';

export interface ChatRequest {
  question: string;
}

export interface ChatResponse {
  answer: string;
  generated_sql: string;
  data_preview: Record<string, unknown>[];
  follow_up_questions?: string[];
}

export interface DashboardOptionsResponse {
  customer_genders: string[];
  customer_states: string[];
  product_categories: string[];
}

export type DashboardMeasure = 'sales_value' | 'sales_quantity';
export type DashboardDimension = 'customer_gender' | 'customer_state' | 'product_category_name';

export interface DashboardChartRequest {
  customer_genders: string[];
  customer_states: string[];
  product_categories: string[];
  selected_dimensions: DashboardDimension[];
  measure: DashboardMeasure;
}

export interface DashboardChart {
  dimension: DashboardDimension;
  title: string;
  image_base64: string;
}

export interface DashboardChartResponse {
  measure: DashboardMeasure;
  charts: DashboardChart[];
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

  async getDashboardOptions(): Promise<DashboardOptionsResponse> {
    const response = await this.client.get<DashboardOptionsResponse>('/dashboard/options');
    return response.data;
  }

  async getDashboardCharts(payload: DashboardChartRequest): Promise<DashboardChartResponse> {
    const response = await this.client.post<DashboardChartResponse>('/dashboard/charts', payload);
    return response.data;
  }
}

export const apiClient = new APIClient();
