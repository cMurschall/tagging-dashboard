

export interface SeekToFunction {
  (time: number): void
}

export interface UseVideoControl {

  seekTo: SeekToFunction
  setSeekTo: (fn: SeekToFunction) => void
}

export class VideoControl implements UseVideoControl {
  private seekToImpl: SeekToFunction

  constructor() {
    this.seekToImpl = (time) => {
      console.warn('[VideoControl] seekTo called before VideoPlayer is ready.')
    }
  }

  public seekTo(time: number): void {
    this.seekToImpl(time)
  }

  public setSeekTo(fn: SeekToFunction): void {
    this.seekToImpl = fn
  }
}
