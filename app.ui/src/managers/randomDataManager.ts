// RandomSpeedDataManager.ts

import { ColumnDefinition, TimeseriesDataPoint, TimeseriesTable } from "@/types/data";
import { Observable } from "../core/observable";
import {  DataManager} from "./dataManager";

export class RandomDataManager extends DataManager {
    measurement$: Observable<TimeseriesDataPoint>;
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
        super();
        this.currentSpeed = initialSpeed;
        this.minSpeed = minSpeed;
        this.maxSpeed = maxSpeed;
        this.accelerationFactor = accelerationFactor;
        this.measurement$ = new Observable();
    }



    getAllMeasurements(): TimeseriesTable {
        const countData = 10000; // Number of data points to generate
        const timestamps = new Float64Array(countData);


        // Create a record mapping each measurement key to a new Float64Array.
        const values: Record<string, Float64Array> = {};
        for (const key of this.measurementKeys) {
            values[key] = new Float64Array(countData);
        }

        for (let i = 0; i < countData; i++) {
            timestamps[i] = i;
            for (const key of this.measurementKeys) {
                values[key][i] = this.currentSpeed + (Math.random() - 0.5) * 2 * this.accelerationFactor;
            }
        }

        return { timestamps, scalarValues: values, vectorValues: {} };
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
                timestamp: 1, values: {
                    speed: this.currentSpeed
                }
            });
        });
    }

    getColumnNames(): ColumnDefinition[] {
        return this.measurementKeys.map(key => {
            return {
                name: key,
                type: "scalar",
                dimension: 1
            };
        });
    }


    getAvailableColumnNames(): Promise<ColumnDefinition[]> {
        return Promise.resolve(this.getColumnNames());
    }
}
