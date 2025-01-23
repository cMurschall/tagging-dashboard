import * as RestClient from './../../services/restclient';



export async function safeFetch<T>(
    fetchFunction: () => Promise<T>
  ): Promise<[Error | null, T | null]> {
    try {
      const data = await fetchFunction();
      return [null, data]; // No error, return data
    } catch (error: any) {
      console.error('API Error:', error.message || error);
      return [error, null]; // Return error, no data
    }
  }
  

export const ApiClient = new RestClient.ProjectEndpointApi(new RestClient.Configuration({
    basePath: 'http://localhost:8888',
}));


// Optionally export all types for convenience
export * from './../../services/restclient';