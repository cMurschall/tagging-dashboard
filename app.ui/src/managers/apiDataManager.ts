// ApiDataManager.ts
import { DataManager, TimeseriesDataPoint } from "./dataManager";
import { Observable } from "./../observable";
import { safeFetch, PlayerApiClient as client } from "../services/utilities";


export class ApiDataManager extends DataManager {

  timeseriesData: TimeseriesDataPoint[] = [];
  measurement$: Observable<TimeseriesDataPoint> = new Observable();


  async initialize(measurementKeys: string[]): Promise<void> {
    const columns = measurementKeys.join(',');
    const [error, response] = await safeFetch(() => client.getDataAsJsonApiV1PlayerDataJsonGet({ columns }));
    if (response) {
      this.timeseriesData = response.data.map((data: any) => {
        const result: TimeseriesDataPoint = { timestamp: data.timestamp, values: {} };

        for (const key of measurementKeys) {
          result.values[key] = data[key];
        }

        return result;
      });
      console.log(`Data ${columns} fetched:`, this.timeseriesData);
    }
    else {
      console.error('Error fetching measurement data:', error);
    }
  }



  subscribeToTimestamp(ts$: Observable<number>): void {
    ts$.subscribe((timestamp: number) => {

      if (this.timeseriesData.length === 0) {
        console.warn('No timeseries data available to subscribe to.');
        return;
      }

      const nearest = this.findNearestDataPoint(this.timeseriesData, timestamp);
      if (!nearest) {
        console.warn('No nearest data point found for timestamp:', timestamp);
        return;
      }

      console.log('Nearest data point found:', nearest);
      this.measurement$.next(nearest);
    });
  }




  getAllMeasurements(): TimeseriesDataPoint[] {
    return this.timeseriesData;
  }

  getColumnNames(): string[] {
    if (this.timeseriesData.length === 0) {
      return [];
    }
    return Object.keys(this.timeseriesData[0].values);
  }
}


