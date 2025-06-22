const API_BASE_URL = 'http://localhost:8000';

export interface AnimationResponse {
  message: string;
  video_urls: string[];
}

export interface UploadResponse {
  success: boolean;
  message?: string;
  error?: string;
}

export class ApiService {
  static async uploadFile(file: File, scope: string): Promise<AnimationResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('scope', scope);

    const response = await fetch(`${API_BASE_URL}/api/create-animation`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to create animation');
    }

    return response.json();
  }

  static getVideoUrl(videoPath: string): string {
    return `${API_BASE_URL}${videoPath}`;
  }
} 