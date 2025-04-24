import * as RestClient from '../../../services/restclient';
import { TestDriveProjectInfoOutput, CreateProjectPayload, TestDriveVideoInfo } from '../../../services/restclient';
import axios from 'axios';
import { isAxiosError } from 'axios';



export async function safeFetch<T>(fetchFunction: () => Promise<T>): Promise<[Error | null, T | null]> {
  try {
    const data = await fetchFunction();
    return [null, data]; // No error, return data
  } catch (error: any) {
    console.error('API Error:', error.message || error);
    return [error, null]; // Return error, no data
  }
}


// export const BasePath = 'http://localhost:8888';
// export const ApiPath = BasePath + '/api/v1';
// export const WebSocketBasePath = "ws://127.0.0.1:8888/api/v1/ws"

export const BasePath = import.meta.env.VITE_BASE_PATH
export const ApiPath = import.meta.env.VITE_API_PATH

const rawWsPath = import.meta.env.VITE_WS_PATH

export const WebSocketBasePath = rawWsPath.startsWith('ws')
  ? rawWsPath
  : `${window.location.protocol === 'https:' ? 'wss://' : 'ws://'}${window.location.host}${import.meta.env.VITE_WS_PATH}`;

console.log("API:", ApiPath);
console.log("WS:", WebSocketBasePath);

export const ProjectApiClient = new RestClient.ProjectEndpointApi(new RestClient.Configuration({
  basePath: BasePath,
}));

export const PlayerApiClient = new RestClient.PlayerEndpointApi(new RestClient.Configuration({
  basePath: BasePath,
}));

export const HealthApiClient = new RestClient.HealthcheckApi(new RestClient.Configuration({
  basePath: BasePath,
}));


export const TagApiClient = new RestClient.TagEndpointApi(new RestClient.Configuration({
  basePath: BasePath,
}));


export type { TestDriveProjectInfoOutput as TestDriveProjectInfo, CreateProjectPayload, TestDriveVideoInfo };

type ProgressCallback = (percentage: number) => void;
const uploadFileWithProgress = async <T>(file: File, endpoint: string, onProgress?: ProgressCallback, fieldName = 'file'): Promise<T> => {
  const formData = new FormData();
  formData.append(fieldName, file);

  const response = await axios.post<T>(endpoint, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (event) => {
      if (event.total && onProgress) {
        const percent = Math.round((event.loaded * 100) / event.total);
        onProgress(percent);
      }
    }
  });
  return response.data;
};

export const uploadCsvFile = (file: File, onProgress?: ProgressCallback): Promise<RestClient.UploadResponse> => {
  const endpoint = `${ApiPath}/project/upload/csv`;
  return uploadFileWithProgress<RestClient.UploadResponse>(file, endpoint, onProgress, 'csv_file');
};


export const uploadVideoFile = (file: File, onProgress?: ProgressCallback): Promise<RestClient.UploadResponse> => {
  const endpoint = `${ApiPath}/project/upload/video`;
  return uploadFileWithProgress<RestClient.UploadResponse>(file, endpoint, onProgress, 'video_file');
};


export const getAxiosErrorMessage = (error: unknown): string => {
  if (isAxiosError(error)) {
    if (error.response?.data?.detail) {
      return error.response.data.detail; // FastAPI-style error
    }
    if (typeof error.response?.data === 'string') {
      return error.response.data;
    }
    return error.message || 'Unknown Axios error';
  }

  if (error instanceof Error) {
    return error.message;
  }

  return String(error) || 'Unknown error';
};
