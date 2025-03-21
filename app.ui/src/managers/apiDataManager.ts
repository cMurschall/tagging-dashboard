// ApiDataManager.ts
import { IDataManager } from "./iDataManager";
import { Observable } from "./../observable";

export interface TimeseriesDataPoint {
  timestamp: number;
  [key: string]: any;
}

export class ApiDataManager implements IDataManager {
  timeseriesData: TimeseriesDataPoint[] = [];
  measurement$: Observable<Record<string, number>> = new Observable();

  private apiUrl: string = "";
  private measurementKeys: string[] = [];

  async initialize(measurementKeys: string[]): Promise<void> {
    this.measurementKeys = measurementKeys;
    // Assume apiUrl is passed earlier or hardcoded
    await this.fetchData(measurementKeys);
  }

  private async fetchData(measurementKeys: string[]): Promise<void> {
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

      const result: Record<string, number> = {};
      for (const key of this.measurementKeys) {
        const raw = nearest[key];
        result[key] = typeof raw === "number" ? raw : Number(raw);
      }

      this.measurement$.next(result);
    });
  }

  constructor(apiUrl: string) {
    this.apiUrl = apiUrl;
  }
}


