import videojs from "video.js";
import Player from 'video.js/dist/types/player';



// Define the options for the FrameByFrameButton
export interface FrameByFrameButtonOptions {
    fps: number;
    value: number;

    children?: any[];
    className?: string;
}

// Get the Button component from Video.js
const Button = videojs.getComponent('Button');

// Define the FrameByFrameButton class
export class FrameByFrameButton extends Button {

    private frameTime: number;
    private step_size: number;

    constructor(player: Player, options: FrameByFrameButtonOptions = { fps: 30, value: 1 }) {
        super(player, options);

        this.frameTime = 1 / options.fps;
        this.step_size = options.value;
    }

    handleClick() {
        console.log('FrameByFrameButton clicked!');
        // Start by pausing the player
        this.player().pause();
        // Calculate movement distance
        const dist = this.frameTime * this.step_size;
        this.player().currentTime((this.player().currentTime() ?? 0) + dist);
    }

    // You might need to override the createEl method if you want more control over the button's structure
    override createEl(): HTMLButtonElement {

        const value = this.options_.value;
        const displayValue = `${value > 0 ? '+' : value < 0 ? '-' : ''}${Math.abs(value)}f`



        const el = super.createEl('button', {
            className: 'vjs-res-button vjs-control',
            innerHTML: `<div class="vjs-control-content"><span class="vjs-fbf">${displayValue}</span></div>`,
            role: 'button',
        });
        return el as HTMLButtonElement;
    }
}

