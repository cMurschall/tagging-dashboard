
import { DataManager, TimeseriesDataPoint, TimeseriesTable } from "./dataManager";
import { Observable } from "./../observable";

export class WebsocketDataManager extends DataManager {
  measurement$: Observable<TimeseriesDataPoint> = new Observable();
  getAllMeasurements(): TimeseriesTable {
    throw new Error("Method not implemented.");
  }
  getColumnNames(): string[] {
    throw new Error("Method not implemented.");
  }
  initialize(measurementKeys: string[]): Promise<void> {
    throw new Error(`Method not implemented: ${measurementKeys}.`);
  }
  subscribeToTimestamp(ts$: Observable<number>): void {
    throw new Error(`Method not implemented: ${ts$}.`);
  }
 
}
