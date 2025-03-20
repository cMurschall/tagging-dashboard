// ApiDataManager.ts
import { IDataManager } from "./iDataManager";
import { Observable } from "./../observable";

export interface TimeseriesDataPoint {
  timestamp: number;
  // additional measurement keys, e.g.:
  [key: string]: any;
}

export class ApiDataManager implements IDataManager {
  timeseriesData: TimeseriesDataPoint[] = [];
  measurement$: Observable<number>;

  constructor(
    public apiUrl: string,
    // The key to lookup the measurement (e.g. "car0_brake_position")
    public measurementKey: string
  ) {
    this.measurement$ = new Observable<number>();
    this.fetchData();
  }

  async fetchData(): Promise<void> {
    try {
      const response = await fetch(this.apiUrl);
      const jsonData = await response.json();
      this.timeseriesData = jsonData.data;
    } catch (error) {
      console.error("Error fetching timeseries data:", error);
    }
  }

  subscribeToTimestamp(ts$: Observable<number>): void {
    ts$.subscribe((timestamp: number) => {
      if (this.timeseriesData.length === 0) return;
      const nearest = this.timeseriesData.reduce((prev, curr) =>
        Math.abs(curr.timestamp - timestamp) <
        Math.abs(prev.timestamp - timestamp)
          ? curr
          : prev
      );
      const measurement = Number(nearest[this.measurementKey]);
      this.measurement$.next(measurement);
    });
  }
}
