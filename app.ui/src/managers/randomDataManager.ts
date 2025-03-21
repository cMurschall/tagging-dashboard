// RandomSpeedDataManager.ts

import { Observable } from "./../observable";
import type { IDataManager } from "./iDataManager";

export class RandomDataManager implements IDataManager {
    measurement$: Observable<Record<string, number>>;
    private currentSpeed: number;
    private minSpeed: number;
    private maxSpeed: number;
    private accelerationFactor: number;

    private measurementKeys: string[] = [];

    /**
     * @param initialSpeed - starting speed (default 0)
     * @param minSpeed - minimum speed (default 0)
     * @param maxSpeed - maximum speed (default 220)
     * @param accelerationFactor - maximum change per update (default 5)
     */
    constructor(
        initialSpeed: number = 0,
        minSpeed: number = 0,
        maxSpeed: number = 220,
        accelerationFactor: number = 5
    ) {
        this.currentSpeed = initialSpeed;
        this.minSpeed = minSpeed;
        this.maxSpeed = maxSpeed;
        this.accelerationFactor = accelerationFactor;
        this.measurement$ = new Observable();
    }
    initialize(measurementKeys: string[]): Promise<void> {
        this.measurementKeys = measurementKeys;
        return Promise.resolve();
    }

    /**
     * Subscribes to a timestamp observable.
     * On each tick, updates the speed by a random delta and emits the new value.
     */
    subscribeToTimestamp(ts$: Observable<number>): void {
        ts$.subscribe(() => {
            // Calculate a random delta in the range [-accelerationFactor, +accelerationFactor]
            const randomDelta = (Math.random() - 0.5) * 2 * this.accelerationFactor;
            let newSpeed = this.currentSpeed + randomDelta;
            // Clamp the new speed between minSpeed and maxSpeed
            newSpeed = Math.max(this.minSpeed, Math.min(this.maxSpeed, newSpeed));
            this.currentSpeed = newSpeed;

            this.measurement$.next({
                speed: newSpeed
            });
        });
    }
}
