
import { findNearestDataPoint, IDataManager, TimeseriesDataPoint } from "./iDataManager";
import { Observable } from "./../observable";

export class WebsocketDataManager implements IDataManager {
  timeseriesData: TimeseriesDataPoint[] = [];
  measurement$: Observable<TimeseriesDataPoint>;
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
  getColumnNames(): string[] {
    return this.measurementKeys;
  }


  getAllMeasurements(): TimeseriesDataPoint[] {
    return this.timeseriesData;
  }



  initialize(measurementKeys: string[]): Promise<void> {
    this.measurementKeys = measurementKeys;
    return Promise.resolve();
  }

  subscribeToTimestamp(ts$: Observable<number>): void {
    ts$.subscribe((timestamp: number) => {
      if (this.timeseriesData.length === 0) return;
      const nearest = findNearestDataPoint(this.timeseriesData, timestamp);
      if (!nearest) return;

      this.measurement$.next(nearest);
    });
  }
}
