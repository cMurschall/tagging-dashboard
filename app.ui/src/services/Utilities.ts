import * as RestClient from './../../services/restclient';
import * as math from 'mathjs'
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



export function throttle<T extends (...args: any[]) => void>(func: T, limit: number): T {
  let lastCall = 0;
  return function (this: any, ...args: any[]) {
    const now = Date.now();
    if (now - lastCall >= limit) {
      lastCall = now;
      func.apply(this, args);
    }
  } as T;
}


export const formatWithTemplate = (value: number, formatTemplate: string) => {
  // Regular expression to find the placeholder and format specifier
  const regex = /\{value(:([A-Za-z]\d*))?\}/;
  const match = formatTemplate.match(regex);

  if (!match) {
    return formatTemplate.replace('{value}', String(value)); // Simple replacement if no format
  }

  const formatSpecifier = match[2];
  let numberFormatOptions = {};

  if (formatSpecifier) {
    const formatType = formatSpecifier.charAt(0).toUpperCase();
    const precision = parseInt(formatSpecifier.slice(1), 10);

    switch (formatType) {
      case 'F': // Fixed-point
        numberFormatOptions = {
          style: 'decimal',
          minimumFractionDigits: isNaN(precision) ? 2 : precision,
          maximumFractionDigits: isNaN(precision) ? 2 : precision,
        };
        break;
      case 'P': // Percent
        numberFormatOptions = {
          style: 'percent',
          minimumFractionDigits: isNaN(precision) ? 0 : precision,
          maximumFractionDigits: isNaN(precision) ? 0 : precision,
        };
        break;
      // Add more cases for other format specifiers as needed (e.g., N for number with grouping)
      default:
        console.warn(`Unsupported format specifier: ${formatSpecifier}`);
    }
  }

  try {
    const formatter = new Intl.NumberFormat('en-US', numberFormatOptions);
    const formattedValue = formatter.format(value);
    return formatTemplate.replace(match[0], formattedValue);
  } catch (error) {
    console.error("Error formatting number:", error);
    return formatTemplate.replace(match[0], String(value));
  }
}



export const transformMathJsValue = (value: number, expression: string) => {
  try {
    const scope = { value };
    return math.evaluate(expression, scope);
  } catch (error) {
    console.error('Error evaluating expression:', error);
    return value; // Return original value on error
  }
};