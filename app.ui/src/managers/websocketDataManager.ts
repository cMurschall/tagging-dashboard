
import { ColumnDefinition, DataManager, TimeseriesDataPoint, TimeseriesTable } from "./dataManager";
import { Observable } from "./../observable";
import { WebSocketDataConnection } from "../services/webSocketDataConnection";
import { ApiDataManager } from "./apiDataManager";
import { TimestampLookup } from "../services/timestampLookup";
import { BufferedTimeseriesTableWriter } from "./bufferedTimeseriesTableWriter";

export class WebsocketDataManager extends DataManager {


  timeseriesData: TimeseriesTable = { timestamps: new Float64Array(), scalarValues: {}, vectorValues: {} };
  measurement$: Observable<TimeseriesDataPoint> = new Observable();
  timestampLookup: TimestampLookup | undefined;


  private measurementKeys: string[] = [];

  bufferedTableWriter: BufferedTimeseriesTableWriter;

  constructor(webSocketDataConnection: WebSocketDataConnection) {
    super();

    this.bufferedTableWriter = new BufferedTimeseriesTableWriter(this.timeseriesData);

    webSocketDataConnection.data$.subscribe((data: TimeseriesDataPoint) => {
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
    this.timestampLookup = new TimestampLookup(this.timeseriesData);
  }


  subscribeToTimestamp(ts$: Observable<number>): void {
    return;
    ts$.subscribe((timestamp: number) => {

      if (this.timeseriesData.timestamps.length === 0) {
        // console.warn('No timeseries data available to subscribe to.');
        return;
      }

      if (!this.timestampLookup) {
        console.warn('Timestamp lookup not initialized.');
        return;
      }

      const nearest = this.timestampLookup.lookup(timestamp);
      if (!nearest) {
        // console.warn('No nearest data point found for timestamp:', timestamp);
        return;
      }

      // console.log(`Nearest data point found for requested ${timestamp}:`, nearest);
      this.measurement$.next(nearest);
    });
  }

}
