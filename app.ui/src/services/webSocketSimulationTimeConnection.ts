
import { BaseWebSocketConnection } from "./baseWebSocketConnection";


export class WebSocketSimulationTimeConnection extends BaseWebSocketConnection<number> {


  protected handleMessage(data: string): void {
    // If simulation time doesn't emit meaningful data, you might ignore this
    const parsed = JSON.parse(data) as Record<string, any>;
    this.data$.next(parsed.timestamp);
  }

  sendCurrentTimeStamp(time: number): void {
    if (this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ timestamp: time }));
    } else {
      console.error("WebSocket is not open. Cannot send message.");
    }
  }
}
