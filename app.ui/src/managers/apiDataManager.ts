// ApiDataManager.ts
import { DataManager, TimeseriesDataPoint, TimeseriesTable } from "./dataManager";
import { Observable } from "./../observable";
import { safeFetch, PlayerApiClient as client } from "../services/utilities";
import { TimestampLookup } from "../services/timestampLookup";


export class ApiDataManager extends DataManager {

  timeseriesData: TimeseriesTable = { timestamps: new Float64Array(), values: {} };
  measurement$: Observable<TimeseriesDataPoint> = new Observable();
  timestampLookup: TimestampLookup | undefined;


  async initialize(measurementKeys: string[]): Promise<void> {
    const columns = measurementKeys.join(',');
    const [error, response] = await safeFetch(() => client.getDataAsJsonApiV1PlayerDataJsonGet({ columns }));
    if (response) {

      const dataList: TimeseriesTable = {
        timestamps: new Float64Array(response.data.length),
        values: Object.fromEntries(
          measurementKeys.map(key => [key, new Float64Array(response.data.length)])
        )
      };
      for (let i = 0; i < response.data.length; i++) {
        const data: any = response.data[i];
        dataList.timestamps[i] = data.timestamp;
        for (const key of measurementKeys) {
          dataList.values[key][i] = data[key];
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

  getColumnNames(): string[] {
    if (this.timeseriesData.timestamps.length === 0) {
      return [];
    }
    return this.timeseriesData.values ? Object.keys(this.timeseriesData.values) : [];
  }
}


