import { TimeseriesDataPoint } from "../managers/dataManager";
import { Observable } from "../observable";

export class WebSocketDataConnection {
  private socket: WebSocket;

  data$: Observable<TimeseriesDataPoint> = new Observable<TimeseriesDataPoint>();

  constructor(url: string) {
    this.socket = new WebSocket(url);

    this.socket.onmessage = (event: MessageEvent) => {
      if (event.data === "ping") {
        // console.log("Received ping, sending pong");
        this.socket.send("pong");
        return;
      }

      const parsed = JSON.parse(event.data) as Record<string, any>;

      const { timestamp, ...rest } = parsed;

      const point: TimeseriesDataPoint = {
        timestamp,
        values: {},
      };

      for (const [key, value] of Object.entries(rest)) {
        point.values[key] = value;
      }

      this.data$.next(point);

    };
  }

}