import { io } from 'socket.io-client';

export class WebSocketService {
  private socket: SocketIOClient.Socket;

  constructor(url: string) {
    this.socket = io(url);  // Replace with your WebSocket server URL
  }

  on(event: string, callback: (data: any) => void) {
    this.socket.on(event, callback);
  }

  emit(event: string, data: any) {
    this.socket.emit(event, data);
  }

  close() {
    this.socket.close();
  }
}
