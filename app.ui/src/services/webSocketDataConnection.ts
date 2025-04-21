import { Tag } from "../../services/restclient";
import { TimeseriesDataPoint } from "../managers/dataManager";
import { BaseWebSocketConnection } from "./baseWebSocketConnection";



export class WebSocketDataConnection extends BaseWebSocketConnection<TimeseriesDataPoint>  {
  protected handleMessage(data: string): void {
    const parsed = JSON.parse(data) as Record<string, any>;
    const { timestamp, ...rest } = parsed;

    const point: TimeseriesDataPoint = {
      timestamp,
      values: {},
    };

    for (const [key, value] of Object.entries(rest)) {
      point.values[key] = value;
    }

    this.data$.next(point);
  }

}