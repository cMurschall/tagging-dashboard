import { Observable } from "../observable";

export interface TimeseriesDataPoint {
  timestamp: number;
  values: Record<string, number>;
}

export interface TimeseriesTable {
  timestamps: Float64Array;
  values: Record<string, Float64Array>;
}

export abstract class DataManager {

  /**
   * Emits values for all user-specified measurement keys.
   * Example: { car0_speed: 123.4, car0_rpm: 2500 }
   */
  abstract measurement$: Observable<TimeseriesDataPoint>;

  /**
   * Returns all measurements.
   */
  abstract getAllMeasurements(): TimeseriesTable;


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

}

