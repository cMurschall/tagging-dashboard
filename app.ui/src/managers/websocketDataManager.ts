
import { IDataManager } from "./iDataManager";
import { Observable } from "./../observable";

export interface TimeseriesDataPoint {
  timestamp: number;
  [key: string]: any;
}

export class WebsocketDataManager implements IDataManager {
  timeseriesData: TimeseriesDataPoint[] = [];
  measurement$: Observable<Record<string, number>>;
  ws: WebSocket;
  measurementKeys: string[] = [];

  constructor(
    public wsUrl: string,
  ) {
    this.measurement$ = new Observable();
    this.ws = new WebSocket(wsUrl);

    this.ws.onmessage = (event: MessageEvent) => {
      try {
        const jsonData = JSON.parse(event.data);
        // Expecting jsonData.data to be an array of timeseries datapoints
        if (jsonData.data && Array.isArray(jsonData.data)) {
          // Append new datapoints
          this.timeseriesData.push(...jsonData.data);
        }
      } catch (error) {
        console.error("Error parsing websocket data:", error);
      }
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
  }
  initialize(measurementKeys: string[]): Promise<void> {
    this.measurementKeys = measurementKeys;
    return Promise.resolve();
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
      // Build the measurement object for all keys
      const measurement: Record<string, number> = {};
      for (const key of this.measurementKeys) {
        const value = nearest[key];
        measurement[key] = typeof value === "number" ? value : Number(value);
      }
      this.measurement$.next(measurement);
    });
  }
}
