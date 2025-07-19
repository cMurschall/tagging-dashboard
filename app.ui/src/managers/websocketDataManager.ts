import { DataManager } from "./dataManager";
import { Observable } from "../core/observable";
import { WebSocketDataConnection } from "../services/webSocketDataConnection";
import { BufferedTimeseriesTableWriter } from "../core/bufferedTimeseriesTableWriter";
import { ColumnDefinition, TimeseriesDataPoint, TimeseriesTable } from "@/types/data";

export class WebsocketDataManager extends DataManager {


  timeseriesData: TimeseriesTable = { timestamps: new Float64Array(), scalarValues: {}, vectorValues: {} };
  measurement$: Observable<TimeseriesDataPoint> = new Observable();
  // timestampLookup: TimestampLookup | undefined;


  private measurementKeys: string[] = [];

  bufferedTableWriter: BufferedTimeseriesTableWriter;

  lastDataPoint: TimeseriesDataPoint | null = null;


  constructor(webSocketDataConnection: WebSocketDataConnection) {
    super();

    this.bufferedTableWriter = new BufferedTimeseriesTableWriter(this.timeseriesData);

    webSocketDataConnection.data$.subscribe((data: TimeseriesDataPoint) => {

      this.lastDataPoint = data;
      // Filter only keys the current instance is interested in
      const filteredValues: Record<string, number | number[]> = {};

      for (const key of this.measurementKeys) {
        if (key in data.values) {
          filteredValues[key] = data.values[key];
        }
      }


      this.bufferedTableWriter.add({
        timestamp: data.timestamp,
        values: filteredValues,
      });

      this.measurement$.next({
        timestamp: data.timestamp,
        values: filteredValues,
      });
    });


  }

  getAllMeasurements(): TimeseriesTable {
    return this.timeseriesData;
  }

  getColumnNames(): ColumnDefinition[] {
    const definitions: ColumnDefinition[] = [];


    // Scalars
    for (const key of Object.keys(this.timeseriesData.scalarValues ?? {})) {
      definitions.push({
        name: key,
        type: "scalar",
        dimension: 1
      });
    }

    // Vectors
    for (const [key, components] of Object.entries(this.timeseriesData.vectorValues ?? {})) {
      definitions.push({
        name: key,
        type: "vector",
        dimension: components.length
      });
    }

    return definitions;
  }
  async initialize(measurementKeys: string[]): Promise<void> {
    this.measurementKeys = measurementKeys;
    // const apiManager = new ApiDataManager();
    // await apiManager.initialize(measurementKeys)

    // this.timeseriesData = apiManager.getAllMeasurements();
    // this.timestampLookup = new TimestampLookup(this.timeseriesData);
  }


  subscribeToTimestamp(_$: Observable<number>): void {
    return;
  }
  getAvailableColumnNames(): Promise<ColumnDefinition[]> {
    return new Promise<ColumnDefinition[]>((resolve) => {
      const intervalTime = 100; // check every 100ms
      const timeout = 4000; // 4 seconds max
      let waited = 0;

      const interval = setInterval(() => {
        if (this.lastDataPoint != null) {
          clearInterval(interval);
          resolve(this.buildColumnDefinitions(this.lastDataPoint));
        } else {
          waited += intervalTime;
          if (waited >= timeout) {
            clearInterval(interval);
            resolve([]); // timeout reached, return empty
          }
        }
      }, intervalTime);
    });
  }

  private buildColumnDefinitions(dataPoint: TimeseriesDataPoint): ColumnDefinition[] {
    const keys = Object.keys(dataPoint.values);
    const definitions: ColumnDefinition[] = [];

    for (const key of keys) {
      const value = dataPoint.values[key];
      if (Array.isArray(value)) {
        definitions.push({
          name: key,
          type: "vector",
          dimension: value.length
        });
      } else {
        definitions.push({
          name: key,
          type: "scalar",
          dimension: 1
        });
      }
    }

    return definitions;
  }


}