import { Observable } from "../observable";


export abstract class BaseWebSocketConnection<T> {
  protected socket!: WebSocket;
  protected url: string;
  protected reconnectIntervalMs = 5000;
  private reconnectTimer: any;

  data$: Observable<T> = new Observable<T>();

  constructor(url: string) {
    this.url = url;
    this.connect();
    this.startReconnectionLoop();
  }

  protected connect(): void {
    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => {
      console.log(`${this.constructor.name} connected`);
    };

    this.socket.onerror = (err) => {
      console.error(`${this.constructor.name} error:`, err);
    };

    this.socket.onclose = () => {
      console.warn(`${this.constructor.name} connection closed`);
    };

    this.socket.onmessage = (event: MessageEvent) => {
      if (event.data === "ping") {
        this.socket.send("pong");
      } else {
        this.handleMessage(event.data);
      }
    };
  }

  protected startReconnectionLoop(): void {
    this.reconnectTimer = setInterval(() => {
      if (this.socket.readyState === WebSocket.CLOSED || this.socket.readyState === WebSocket.CLOSING) {
        console.log(`${this.constructor.name} attempting to reconnect...`);
        this.connect();
      }
    }, this.reconnectIntervalMs);
  }

  stopReconnectionLoop(): void {
    clearInterval(this.reconnectTimer);
  }


  close(): void {
    this.stopReconnectionLoop();
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.close();
    }
    console.log(`${this.constructor.name} manually closed`);
  }

  protected abstract handleMessage(data: string): void;
}
