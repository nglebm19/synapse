/**
 * API service for communicating with the Synapse backend
 */

const API_BASE_URL = 'http://localhost:8000/api';

export interface ProcessVideoRequest {
  video_url: string;
  user_id?: string;
}

export interface ProcessVideoResponse {
  job_id: string;
  status: string;
  message: string;
  estimated_time?: number;
}

export interface JobStatusResponse {
  job_id: string;
  status: string;
  progress: number;
  current_step?: string;
  error_message?: string;
  created_at: string;
  estimated_remaining?: number;
}

export interface JobResultsResponse {
  job_id: string;
  status: string;
  video_title: string;
  video_url: string;
  transcript: string;
  summary: string;
  processing_time?: number;
  created_at: string;
  completed_at?: string;
}

export interface HealthResponse {
  status: string;
  message: string;
  models: {
    whisper_loaded: boolean;
    summarization_loaded: boolean;
    device: string;
  };
  system_info: {
    device: string;
    cache_dir: string;
  };
}

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }

  async healthCheck(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  async processVideo(videoUrl: string, userId?: string): Promise<ProcessVideoResponse> {
    return this.request<ProcessVideoResponse>('/process-video', {
      method: 'POST',
      body: JSON.stringify({
        video_url: videoUrl,
        user_id: userId,
      }),
    });
  }

  async getJobStatus(jobId: string): Promise<JobStatusResponse> {
    return this.request<JobStatusResponse>(`/job-status/${jobId}`);
  }

  async getJobResults(jobId: string): Promise<JobResultsResponse> {
    return this.request<JobResultsResponse>(`/job-results/${jobId}`);
  }

  async getUserJobs(userId?: string): Promise<any[]> {
    const queryParam = userId ? `?user_id=${userId}` : '';
    return this.request<any[]>(`/jobs${queryParam}`);
  }

  // Utility method to poll job status until completion
  async pollJobStatus(
    jobId: string,
    onProgress: (status: JobStatusResponse) => void,
    pollInterval: number = 2000
  ): Promise<JobResultsResponse> {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const status = await this.getJobStatus(jobId);
          onProgress(status);

          if (status.status === 'completed') {
            const results = await this.getJobResults(jobId);
            resolve(results);
          } else if (status.status === 'failed') {
            reject(new Error(status.error_message || 'Job failed'));
          } else {
            // Continue polling
            setTimeout(poll, pollInterval);
          }
        } catch (error) {
          reject(error);
        }
      };

      poll();
    });
  }
}

export const apiService = new ApiService();

