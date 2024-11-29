export interface DataPayload {
  timestamp: number;
  data: Record<string, any>;
}

export interface PlayerState {
  isPlaying: boolean;
  currentTime: number;
}

export abstract class BaseVisualization {
  abstract onDataLoaded(data: DataPayload): void;
  abstract onPlayerStateChange(newState: PlayerState): void;
  abstract onTimeUpdate(currentTime: number): void;

  play(): void {}
  pause(): void {}
  seek(time: number): void {}
}