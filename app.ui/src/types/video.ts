import Player from 'video.js/dist/types/player';

export interface SeekToFunction {
    (time: number): void
  }

  export interface UseVideoControl {

    seekTo: SeekToFunction
    setSeekTo: (fn: SeekToFunction) => void
  }




export interface VideoPlayer extends Player {
  spriteThumbnails: (options: any) => void;
}



// Define the options for the FrameByFrameButton
export interface FrameByFrameButtonOptions {
    fps: number;
    value: number;

    children?: any[];
    className?: string;
}