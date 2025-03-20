import { Observable } from "../observable";


export interface IChartDataManager {
  // An observable that emits the current measurement (e.g. a number)
  measurement$: Observable<number>;

  /**
   * Subscribes to an external timestamp observable.
   * When a new timestamp is emitted, the manager finds the nearest datapoint and
   * emits the corresponding measurement via its measurement$ observable.
   */
  subscribeToTimestamp(ts$: Observable<number>): void;
}
