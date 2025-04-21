// websocketHandler.ts
import WebSocket from 'ws';
import streamDeck from "@elgato/streamdeck";

export class WebSocketHandler {
  private socket: WebSocket | null = null;
  private latestTimestamp: number | null = null;


  protected reconnectIntervalMs = 2500;
  private reconnectTimer: any;

  constructor(private url: string) {

    this.url = url;
    this.connect();
    this.startReconnectionLoop();
  }



  connect(): void {

    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      streamDeck.logger.warn("WebSocket already connected.");
      return;
    }

    streamDeck.logger.info("Connecting to", this.url);
    this.socket = new WebSocket(this.url);



    this.socket.onopen = () => {
      streamDeck.logger.info("WebSocket connected.");
    };

    this.socket.onmessage = (event: WebSocket.MessageEvent) => {
      try {
        const data = JSON.parse(event.data.toString());

        if (data === "ping") {
          this.send("pong");
        } else if (typeof data === 'object' && data.timestamp) {
          this.latestTimestamp = data.timestamp;
          // streamDeck.logger.info("Updated timestamp:", this.latestTimestamp);
        }
      } catch (e) {
        streamDeck.logger.error("Failed to process message:", event.data);
      }
    };

    this.socket.onerror = (err: any) => {
      streamDeck.logger.error("WebSocket error:", err);
    };

    this.socket.onclose = () => {
      streamDeck.logger.info("WebSocket closed. Reconnecting in", this.reconnectIntervalMs, "ms...");
    };
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  send(data: any): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(typeof data === "string" ? data : JSON.stringify(data));
    } else {
      streamDeck.logger.warn("WebSocket not connected. Cannot send message.");
    }
  }

  getLatestTimestamp(): number | null {
    return this.latestTimestamp;
  }

  setUrl(newUrl: string): void {
    if (this.url != newUrl) {
      streamDeck.logger.info("Changing WebSocket URL to:", newUrl);
      this.url = newUrl;
      this.stopReconnectionLoop();
      this.disconnect();
      this.connect();
      this.startReconnectionLoop();
    }
  }

  isConnected(): boolean {
    return this.socket !== null && this.socket.readyState === WebSocket.OPEN;
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
}
