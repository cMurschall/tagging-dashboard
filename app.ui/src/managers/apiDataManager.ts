// ApiDataManager.ts
import { findNearestDataPoint, IDataManager, TimeseriesDataPoint } from "./iDataManager";
import { Observable } from "./../observable";
import { safeFetch, PlayerApiClient as client } from "../services/Utilities";


export class ApiDataManager implements IDataManager {
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
      if (this.timeseriesData.length === 0) return;

      const nearest = findNearestDataPoint(this.timeseriesData, timestamp);
      if (!nearest) return;

      this.measurement$.next(nearest);
    });
  }




  getAllMeasurements(): TimeseriesDataPoint[] {
    return this.timeseriesData;
  }
}


