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

export const IDENTITY_EXPRESSION = 'value';

export const BasePath = 'http://localhost:8888';
export const ApiPath = BasePath + '/api/v1';
export const WebSocketBasePath = "ws://127.0.0.1:8888/api/v1/ws"


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

const formatRegExp = new RegExp(`\\{${IDENTITY_EXPRESSION}(?::([A-Za-z]\\d*))?\\}`);
export const formatWithTemplate = (value: number, formatTemplate: string): string => {
  if (!formatTemplate || formatTemplate.trim() === IDENTITY_EXPRESSION) {
    return String(value);
  }
  // Match against the template
  const match = formatTemplate.match(formatRegExp);

  // Replace fallback, using the same constant again
  if (!match) {
    return formatTemplate.replace(`{${IDENTITY_EXPRESSION}}`, String(value));
  }

  const formatSpecifier = match[1];
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
      case 'N':
        numberFormatOptions = {
          style: 'decimal',
          useGrouping: true,
          minimumFractionDigits: isNaN(precision) ? 0 : precision,
          maximumFractionDigits: isNaN(precision) ? 0 : precision,
        };
        break;
      case 'E':
        const expPrecision = isNaN(precision) ? 2 : precision;
        const exponentialValue = value.toExponential(expPrecision);
        return formatTemplate.replace(match[0], exponentialValue);

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


// const compiledExpressions: { [expression: string]: math.EvalFunction } = {};
const compiledExpressions = new Map<string, math.EvalFunction>();
export const transformMathJsValue = (value: number, expression: string): number => {
  if (!expression || expression.trim() === IDENTITY_EXPRESSION) {
    return value;
  }
  try {
    // Check if the expression has already been compiled
    if (!compiledExpressions.has(expression)) {
      // Compile the expression and store it
      compiledExpressions.set(expression, math.compile(expression));
    }

    // Retrieve the compiled expression
    const compiledExpression = compiledExpressions.get(expression)!;

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
      if (typeof dp.values[key] === 'number') {
        values[key].push(dp.values[key]);
      }
      if (Array.isArray(dp.values[key])) {
        values[key].push(...dp.values[key]);
      }
    }
  }
  const denseValues: Record<string, Float64Array> = {};
  for (const key in values) {
    denseValues[key] = new Float64Array(values[key]);
  }
  return { timestamps, scalarValues: denseValues, vectorValues: {} };
}



export interface TimestampStatistics {
  count: number;
  min: number;
  max: number;
  duration: number;
  meanInterval: number;
  medianInterval: number;
  minInterval: number;
  maxInterval: number;
  uniform: boolean;
}


export function getTimestampStatistics(table: TimeseriesTable): TimestampStatistics {
  const ts = table.timestamps;
  const count = ts.length;

  if (count < 2) {
    return {
      count,
      min: ts[0] ?? NaN,
      max: ts[0] ?? NaN,
      duration: 0,
      meanInterval: 0,
      medianInterval: 0,
      minInterval: 0,
      maxInterval: 0,
      uniform: true
    };
  }

  const min = ts[0];
  const max = ts[ts.length - 1];
  const duration = max - min;

  const intervals: number[] = [];
  for (let i = 1; i < ts.length; i++) {
    intervals.push(ts[i] - ts[i - 1]);
  }

  const meanInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;

  const sortedIntervals = [...intervals].sort((a, b) => a - b);
  const mid = Math.floor(sortedIntervals.length / 2);
  const medianInterval = sortedIntervals.length % 2 === 0
    ? (sortedIntervals[mid - 1] + sortedIntervals[mid]) / 2
    : sortedIntervals[mid];

  const minInterval = sortedIntervals[0];
  const maxInterval = sortedIntervals[sortedIntervals.length - 1];

  const tolerance = 1e-9;
  const uniform = maxInterval - minInterval < tolerance;

  return {
    count,
    min,
    max,
    duration,
    meanInterval,
    medianInterval,
    minInterval,
    maxInterval,
    uniform
  };
}

export const clamp = (val: number, min: number, max: number) => Math.min(Math.max(val, min), max)