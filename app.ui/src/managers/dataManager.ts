import { Observable } from "../core/observable";

export interface TimeseriesDataPoint {
  timestamp: number;
  values: Record<string, number | number[]>;
}

export interface TimeseriesTable {
  timestamps: Float64Array;

  scalarValues: Record<string, Float64Array>;
  vectorValues: Record<string, Float64Array[]>; // each index = 1 timestep
}


export interface ColumnDefinition {
  name: string;         // e.g. "car0_rpm" or "vehicle_pos"
  type: "scalar" | "vector";
  dimension: number;    // 1 for scalar, >1 for vectors
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
  abstract getColumnNames(): ColumnDefinition[]

  /**
   * User defines which measurements they're interested in.
   */
  abstract initialize(measurementKeys: string[]): Promise<void>

  /**
   * Emits the closest values to each incoming timestamp.
   */
  abstract subscribeToTimestamp(ts$: Observable<number>): void;

}


export class EmptyDataManager extends DataManager {
  measurement$ = new Observable<TimeseriesDataPoint>();
  getAllMeasurements(): TimeseriesTable {
    return { timestamps: new Float64Array(), scalarValues: {}, vectorValues: {} };
  }
  getColumnNames(): ColumnDefinition[] {
    return [];
  }
  initialize(_measurementKeys: string[]): Promise<void> {
    return Promise.resolve();
  }
  subscribeToTimestamp(_ts$: Observable<number>): void {
    throw new Error("Method not implemented.");
  }
}




