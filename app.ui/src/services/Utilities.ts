import * as RestClient from './../../services/restclient';
import { TestDriveProjectInfoOutput, CreateProjectPayload, TestDriveVideoInfo } from './../../services/restclient';



export async function safeFetch<T>(fetchFunction: () => Promise<T>): Promise<[Error | null, T | null]> {
  try {
    const data = await fetchFunction();
    return [null, data]; // No error, return data
  } catch (error: any) {
    console.error('API Error:', error.message || error);
    return [error, null]; // Return error, no data
  }
}

// export async function safeFetch<T>(fetchFunction: () => Promise<Response>): Promise<[Error | null, T | null]> {
//   try {
//     const response = await fetchFunction();

//     // Check if the HTTP status is not OK
//     if (!response.ok) {
//       const error = new Error(`HTTP error! Status: ${response.status} - ${response.statusText}`);
//       // console.error('API Error:', error.message);
//       throw error;
//     }

//     // Parse the response as JSON (or any other expected format)
//     const data: T = await response.json();
//     return [null, data]; // No error, return data
//   } catch (error: any) {
//     // console.error('API Error:', error.message || error);
//     return [error, null]; // Return error, no data
//   }
// }

export const BasePath = 'http://localhost:8888';
export const ApiPath = BasePath + '/api/v1';


export const ProjectApiClient = new RestClient.ProjectEndpointApi(new RestClient.Configuration({
  basePath: BasePath,
}));

export const PlayerApiClient = new RestClient.PlayerEndpointApi(new RestClient.Configuration({
  basePath: BasePath,
}));

export const HealthApiClient = new RestClient.HealthcheckApi(new RestClient.Configuration({
  basePath: BasePath,
}));


export type { TestDriveProjectInfoOutput as TestDriveProjectInfo, CreateProjectPayload, TestDriveVideoInfo };
