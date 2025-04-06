import { Observable } from "../observable";

export interface TimeseriesDataPoint {
  timestamp: number;
  values: Record<string, number>;
}


export abstract class DataManager {
  /**
   * Emits values for all user-specified measurement keys.
   * Example: { car0_speed: 123.4, car0_rpm: 2500 }
   */
  abstract measurement$: Observable<TimeseriesDataPoint>;

  /**
   * Returns all measurements.
   * Example: [{ car0_speed: 123.4, car0_rpm: 2500 }, ...]
   */
  abstract getAllMeasurements(): TimeseriesDataPoint[];


  /**
   * Returns the names of all measurements.
   * Example: ['car0_speed', 'car0_rpm']
   */
  abstract getColumnNames(): string[]

  /**
   * User defines which measurements they're interested in.
   */
  abstract initialize(measurementKeys: string[]): Promise<void>

  /**
   * Emits the closest values to each incoming timestamp.
   */
  abstract subscribeToTimestamp(ts$: Observable<number>): void;


  private fallbackThreshold = 0.5; // 500ms
  findNearestDataPoint(timeseriesData: TimeseriesDataPoint[], actualTimestamp: number): TimeseriesDataPoint | null {
    const n = timeseriesData.length;
    if (n === 0) return null;

    const firstTimestamp = timeseriesData[0].timestamp;
    const lastTimestamp = timeseriesData[n - 1].timestamp;

    // check if in range
    if (actualTimestamp < firstTimestamp) return null;
    if (actualTimestamp > lastTimestamp) return null;

    const avgStep = (lastTimestamp - firstTimestamp) / (n - 1);
    let estimatedIndex = Math.floor((actualTimestamp - firstTimestamp) / avgStep);
    estimatedIndex = Math.max(0, Math.min(n - 1, estimatedIndex));


    // Search in a small window around the estimated index
    const searchRadius = 5;
    let bestIndex = estimatedIndex;
    let bestDiff = Math.abs(timeseriesData[estimatedIndex].timestamp - actualTimestamp);


    const start = Math.max(0, estimatedIndex - searchRadius);
    const end = Math.min(n - 1, estimatedIndex + searchRadius);

    for (let i = start; i <= end; i++) {
      const diff = Math.abs(timeseriesData[i].timestamp - actualTimestamp);
      if (diff < bestDiff) {
        bestDiff = diff;
        bestIndex = i;
      }
    }

    // If the best diff is too large, fallback to full binary search
    if (bestDiff > this.fallbackThreshold) {
      bestIndex = this.binarySearchNearestIndex(timeseriesData, actualTimestamp);
    }

    return timeseriesData[bestIndex];
  }



  binarySearchNearestIndex(data: TimeseriesDataPoint[], target: number): number {
    let low = 0;
    let high = data.length - 1;

    while (low <= high) {
      const mid = Math.floor((low + high) / 2);
      const midTime = data[mid].timestamp;

      if (midTime === target) return mid;
      if (midTime < target) low = mid + 1;
      else high = mid - 1;
    }

    // low is now the index of the first value > target
    // high is the last value < target
    const lowDiff = low < data.length ? Math.abs(data[low].timestamp - target) : Infinity;
    const highDiff = high >= 0 ? Math.abs(data[high].timestamp - target) : Infinity;

    if (lowDiff < highDiff) return low;
    return high;
  }
}

