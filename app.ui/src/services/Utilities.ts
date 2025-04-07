import * as RestClient from '../../services/restclient';
import * as math from 'mathjs'
import { TestDriveProjectInfoOutput, CreateProjectPayload, TestDriveVideoInfo } from '../../services/restclient';
import { TimeseriesDataPoint, TimeseriesTable } from '../managers/dataManager';



export async function safeFetch<T>(fetchFunction: () => Promise<T>): Promise<[Error | null, T | null]> {
  try {
    const data = await fetchFunction();
    return [null, data]; // No error, return data
  } catch (error: any) {
    console.error('API Error:', error.message || error);
    return [error, null]; // Return error, no data
  }
}


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


export const formatWithTemplate = (value: number, formatTemplate: string): string => {
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

const compiledExpressions: { [expression: string]: math.EvalFunction } = {};
export const transformMathJsValue = (value: number, expression: string): number => {
  try {
    // Check if the expression has already been compiled
    if (!compiledExpressions[expression]) {
      // Compile the expression and store it
      compiledExpressions[expression] = math.compile(expression);
    }

    // Retrieve the compiled expression
    const compiledExpression = compiledExpressions[expression];

    // Evaluate the compiled expression with the scope
    const scope = { value };
    const evaluated = compiledExpression.evaluate(scope);

    return evaluated as number;
  } catch (error) {
    console.error('Error evaluating expression:', error);
    return value; // Return original value on error
  }
};

export const transformMathJsValueNoCompile = (value: number, expression: string): number => {
  try {
    const scope = { value };
    const evaluated = math.evaluate(expression, scope);
    return evaluated as number;
  } catch (error) {
    console.error('Error evaluating expression:', error);
    return value; // Return original value on error
  }
};



export const areArraysSameUnordered = <T>(arr1: T[], arr2: T[]): boolean => {
  if (arr1.length !== arr2.length) {
    return false;
  }
  const set1 = new Set(arr1);
  const set2 = new Set(arr2);
  return !(arr1.some(item => !set2.has(item)) || arr2.some(item => !set1.has(item)));
}


// check if we are in development mode
export const isDevMode = (): boolean => {
  return import.meta.env.MODE == 'development';
};



// Helper function to convert an array of TimeseriesDataPoint into a TimeseriesTable.
export const toDenseTable = (dataPoints: TimeseriesDataPoint[]): TimeseriesTable => {
  const timestamps = new Float64Array(dataPoints.map((dp) => dp.timestamp));
  const values: Record<string, number[]> = {};
  for (const dp of dataPoints) {
    for (const key in dp.values) {
      if (!values[key]) {
        values[key] = [];
      }
      values[key].push(dp.values[key]);
    }
  }
  const denseValues: Record<string, Float64Array> = {};
  for (const key in values) {
    denseValues[key] = new Float64Array(values[key]);
  }
  return { timestamps, values: denseValues };
}