// websocketHandler.ts
import WebSocket from 'ws';
import streamDeck from "@elgato/streamdeck";

export class WebSocketHandler {
  private socket: WebSocket | null = null;
  private latestTimestamp: number | null = null;
  private reconnectIntervalMs: number = 5000;
  private reconnectTimeout: NodeJS.Timeout | null = null;

  constructor(private url: string) { }

  connect(): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      streamDeck.logger.warn("WebSocket already connected.");
      return;
    }

    streamDeck.logger.info("Connecting to", this.url);
    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => {
      streamDeck.logger.info("WebSocket connected.");
      this.clearReconnectTimeout();
    };

    this.socket.onmessage = (event: WebSocket.MessageEvent) => {
      try {
        const data = JSON.parse(event.data.toString());

        if (data === "ping") {
          this.send("pong");
        } else if (typeof data === 'object' && data.timestamp) {
          this.latestTimestamp = data.timestamp;
          streamDeck.logger.info("Updated timestamp:", this.latestTimestamp);
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
      this.scheduleReconnect();
    };
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.clearReconnectTimeout();
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
      this.disconnect();
      this.connect();
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimeout) return;

    this.reconnectTimeout = setTimeout(() => {
      this.connect();
    }, this.reconnectIntervalMs);
  }

  private clearReconnectTimeout(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
  }
}
