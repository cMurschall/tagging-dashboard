// ApiDataManager.ts
import { ColumnDefinition, DataManager, TimeseriesDataPoint, TimeseriesTable } from "./dataManager";
import { Observable } from "./../observable";
import { safeFetch, PlayerApiClient as client } from "../services/utilities";
import { TimestampLookup } from "../services/timestampLookup";


export class ApiDataManager extends DataManager {

  timeseriesData: TimeseriesTable = { timestamps: new Float64Array(), scalarValues: {}, vectorValues: {} };
  measurement$: Observable<TimeseriesDataPoint> = new Observable();
  timestampLookup: TimestampLookup | undefined;


  async initialize(measurementKeys: string[]): Promise<void> {
    const columns = measurementKeys.join(',');
    const [error, response] = await safeFetch(() => client.getDataAsJsonApiV1PlayerDataJsonGet({ columns }));
    if (response) {

      const dataList: TimeseriesTable = {
        timestamps: new Float64Array(response.data.length),
        scalarValues: {},
        vectorValues: {},
      };

      const first = response.data[0] as any
      const scalarKeys: string[] = [];
      const vectorKeys: string[] = [];

      for (const key of measurementKeys) {
        const value = first[key];
        let parsed: number[] | null = null;

        if (Array.isArray(value)) {
          parsed = value;
        } else if (typeof value === "string" && value.includes(",")) {
          // Try parsing as a number array
          parsed = value.split(",").map(Number);
          if (parsed.some(isNaN)) {
            parsed = null; // fallback if not all are valid numbers
          }
        }

        if (parsed && parsed.length > 0) {
          vectorKeys.push(key);
          const dims = parsed.length;
          dataList.vectorValues[key] = Array.from({ length: dims }, () => new Float64Array(response.data.length));
        } else {
          scalarKeys.push(key);
          dataList.scalarValues[key] = new Float64Array(response.data.length);
        }
      }

      // 2. Fill in data
      for (let i = 0; i < response.data.length; i++) {
        const data: any = response.data[i];
        dataList.timestamps[i] = data.timestamp;

        for (const key of scalarKeys) {
          dataList.scalarValues[key][i] = data[key];
        }

        for (const key of vectorKeys) {
          const raw = data[key];
          const vector: number[] = Array.isArray(raw)
            ? raw
            : typeof raw === "string"
              ? raw.split(",").map((v) => Number(v.trim()))
              : [];

          for (let d = 0; d < vector.length; d++) {
            dataList.vectorValues[key][d][i] = vector[d];
          }
        }
      }


      this.timeseriesData = dataList;
      console.log(`Data ${columns} fetched:`, this.timeseriesData);
      this.timestampLookup = new TimestampLookup(this.timeseriesData);
    }
    else {
      console.error('Error fetching measurement data:', error);
    }
  }



  subscribeToTimestamp(ts$: Observable<number>): void {
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




  getAllMeasurements(): TimeseriesTable {
    return this.timeseriesData;
  }

  getColumnNames(): ColumnDefinition[] {
    if (this.timeseriesData.timestamps.length === 0) {
      return [];
    }
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
}


