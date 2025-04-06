/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';

// --- Mock the Video.js module before importing our class --- //
vi.mock('video.js', () => {
    // Define a dummy Button class that our FrameByFrameButton will extend.
    class DummyButton {
      options_: any;
      _player: any;
      constructor(player: any, options: any) {
        this._player = player;
        this.options_ = options;
      }
      player() {
        return this._player;
      }
      createEl(
        type = 'div',
        props: { className?: string; innerHTML?: string; role?: string } = {}
      ) {
        const el = document.createElement(type);
        if (props.className) {
          el.className = props.className;
        }
        if (props.innerHTML) {
          el.innerHTML = props.innerHTML;
        }
        if (props.role) {
          el.setAttribute('role', props.role);
        }
        return el;
      }
    }
  
    return {
      default: {
        getComponent: (name: string) => {
          if (name === 'Button') {
            return DummyButton;
          }
          throw new Error(`Component ${name} not found`);
        }
      }
    };
  });

// --- Now import the class to test --- //
import { FrameByFrameButton } from './../../services/frameByFrameButton';

// A helper to create a fake player with pause and currentTime methods.
function createFakePlayer(initialTime = 0) {
  return {
    _currentTime: initialTime,
    pause: vi.fn(),
    currentTime(time?: number) {
      if (typeof time === 'number') {
        this._currentTime = time;
      }
      return this._currentTime;
    }
  };
}

describe('FrameByFrameButton', () => {
  let fakePlayer: any;

  beforeEach(() => {
    fakePlayer = createFakePlayer(10); // start at 10 seconds
  });

  describe('handleClick', () => {
    it('should pause the player and advance the current time correctly', () => {
      const fps = 30;
      const value = 2;
      const expectedIncrement = (1 / fps) * value; // 2/30 seconds

      // Create an instance with the fake player
      const button = new FrameByFrameButton(fakePlayer, { fps, value });
      
      // Call handleClick to simulate a button click.
      button.handleClick();

      // Verify that the player's pause method was called.
      expect(fakePlayer.pause).toHaveBeenCalled();

      // Verify that the currentTime was advanced by the expected increment.
      const newTime = fakePlayer.currentTime();
      expect(newTime).toBeCloseTo(10 + expectedIncrement);
    });
  });

  describe('createEl', () => {
    it('should create a button element with correct inner HTML for a positive value', () => {
      const value = 2;
      const button = new FrameByFrameButton(fakePlayer, { fps: 30, value });
      const el = button.createEl();

      // The element should be a BUTTON.
      expect(el.tagName).toBe('BUTTON');
      // Check that the inner HTML contains the correct formatted text (e.g. "+2f").
      expect(el.innerHTML).toContain('<span class="vjs-fbf">+2f</span>');
    });

    it('should create a button element with correct inner HTML for a negative value', () => {
      const value = -3;
      const button = new FrameByFrameButton(fakePlayer, { fps: 30, value });
      const el = button.createEl();

      expect(el.tagName).toBe('BUTTON');
      expect(el.innerHTML).toContain('<span class="vjs-fbf">-3f</span>');
    });

    it('should create a button element with correct inner HTML for a zero value', () => {
      const value = 0;
      const button = new FrameByFrameButton(fakePlayer, { fps: 30, value });
      const el = button.createEl();

      expect(el.tagName).toBe('BUTTON');
      expect(el.innerHTML).toContain('<span class="vjs-fbf">0f</span>');
    });
  });
});
