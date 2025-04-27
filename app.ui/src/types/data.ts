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
