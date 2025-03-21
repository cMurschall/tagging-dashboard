import { Observable } from "../observable";


export interface IDataManager {
  /**
   * Emits values for all user-specified measurement keys.
   * Example: { car0_speed: 123.4, car0_rpm: 2500 }
   */
  measurement$: Observable<Record<string, number>>;

  /**
   * User defines which measurements they're interested in.
   */
  initialize(measurementKeys: string[]): Promise<void>

  /**
   * Emits the closest values to each incoming timestamp.
   */
  subscribeToTimestamp(ts$: Observable<number>): void;
}
