import { TimeseriesDataPoint, TimeseriesTable } from "../managers/dataManager";

// the tolerance for checking even spacing (e.g., 1% of the average step)
const EVEN_SPACING_TOLERANCE_FACTOR = 0.01;
// the tolerance factor for the final proximity check
const FINAL_PROXIMITY_FACTOR = 1.5;

export class TimestampLookup {

    private table: TimeseriesTable;

    private startTime: number;
    private averageStep: number;
    private lastIndex: number;
    private lastTimestamp: number;
    private rowCount: number;

    // Flags to store the results of the checks
    private isSorted: boolean;
    private isEvenlySpaced: boolean;

    private stats: Record<string, { count: number; totalTime: number }> = {
        forward: { count: 0, totalTime: 0 },
        reverse: { count: 0, totalTime: 0 },
        interpolate: { count: 0, totalTime: 0 },
        binary: { count: 0, totalTime: 0 },
    };


    constructor(table: TimeseriesTable) {
        this.table = table;
        this.rowCount = table.timestamps.length;

        if (this.rowCount === 0) {
            this.startTime = 0;
            this.averageStep = 0;
            this.isSorted = true; // Empty array is considered sorted
            this.isEvenlySpaced = true; // And evenly spaced
        } else {
            // --- 1. Check if timestamps are sorted ---
            this.isSorted = this.checkSorting();
            if (!this.isSorted) {
                // Critical error: The lookup logic relies on sorted timestamps.
                console.error("TimestampLookup Error: Timestamps are not sorted!");
                // Depending on requirements, you might throw an error instead:
                // throw new Error("TimestampLookup Error: Timestamps must be sorted.");
            }

            this.startTime = table.timestamps[0];
            const endTime = this.rowCount > 1 ? table.timestamps[this.rowCount - 1] : this.startTime;
            this.averageStep = this.rowCount > 1 ? (endTime - this.startTime) / (this.rowCount - 1) : 0;

            // --- 2. Check if timestamps are evenly spaced ---
            // Only check spacing if sorted and there's more than one point
            if (this.isSorted && this.rowCount > 1) {
                const tolerance = this.averageStep * EVEN_SPACING_TOLERANCE_FACTOR;
                this.isEvenlySpaced = this.checkEvenSpacing(tolerance);
                if (!this.isEvenlySpaced) {
                    console.warn("TimestampLookup Warning: Timestamps are not evenly spaced. Lookup might be less efficient.");
                }
            } else {
                // If not sorted or only one point, consider it not evenly spaced for lookup purposes
                this.isEvenlySpaced = this.rowCount <= 1;
            }
        }

        // Initialize last known position
        this.lastIndex = 0;
        this.lastTimestamp = this.startTime;
    }


    getStats() {
        const summary: Record<string, string> = {};

        for (const key in this.stats) {
            const stat = this.stats[key];
            const avg = stat.count > 0 ? (stat.totalTime / stat.count).toFixed(4) : "0";
            summary[key] = `${stat.count} calls, avg ${avg} ms`;
        }
        return summary;
    }


    lookup(targetTs: number): TimeseriesDataPoint | null {

        const startTimePerf = performance.now();
        // Basic checks
        if (this.rowCount === 0) {
            return null;
        }
        if(this.rowCount === 1) {
            return this.getDataPoint(0); // Return the only data point available
        }
        // If data wasn't sorted, return null or handle as an error state
        if (!this.isSorted) {
            console.error("Cannot perform lookup on unsorted timestamps.");
            return null; // Or throw an error
        }

        // -Conditional Logic based on Even Spacing 
        if (!this.isEvenlySpaced) {
            // If timestamps are not evenly spaced (or not sorted), skip optimizations and use binary search directly.
            const fallbackIndex = this.binarySearchClosest(targetTs);
            return this.finalize("binary", targetTs, fallbackIndex, startTimePerf);
        }

        const maxScanDelta = this.averageStep * 3;
        let index = this.lastIndex;

        // Forward Replay (most common case)
        const isForward = targetTs >= this.lastTimestamp && targetTs - this.lastTimestamp <= maxScanDelta
        if (isForward) {
            while (index < this.rowCount - 1 && this.table.timestamps[index + 1] <= targetTs) {
                index++;
            }
            return this.finalize("forward", targetTs, index, startTimePerf);
        }


        //  Reverse Scrubbing 
        const isReverse = targetTs < this.lastTimestamp && this.lastTimestamp - targetTs <= maxScanDelta
        if (isReverse) {
            while (index > 0 && this.table.timestamps[index - 1] >= targetTs) {
                index--;
            }
            return this.finalize("reverse", targetTs, index, startTimePerf);
        }


        // Interpolation Guess
        const estimatedIndex = Math.floor((targetTs - this.startTime) / this.averageStep);
        const scanRange = 3;
        const searchStart = Math.max(0, estimatedIndex - scanRange);
        const searchEnd = Math.min(this.rowCount - 1, estimatedIndex + scanRange);

        if (searchStart <= searchEnd) {
            let bestIndex = searchStart;
            let bestDiff = Math.abs(this.table.timestamps[bestIndex] - targetTs);

            for (let i = searchStart + 1; i <= searchEnd; i++) {
                const diff = Math.abs(this.table.timestamps[i] - targetTs);
                if (diff < bestDiff) {
                    bestDiff = diff;
                    bestIndex = i;
                }
            }
            return this.finalize("interpolate", targetTs, bestIndex, startTimePerf);
        }

        // Binary Search Fallback
        const fallbackIndex = this.binarySearchClosest(targetTs);
        return this.finalize("binary", targetTs, fallbackIndex, startTimePerf);
    }


    private finalize(method: string, targetTs: number, foundIndex: number, startPerf: number): TimeseriesDataPoint | null {
        // Ensure index is valid after lookup logic
        const index = Math.max(0, Math.min(this.rowCount - 1, foundIndex));

        // Get the actual timestamp found at the index
        const actualTs = this.table.timestamps[index];

        // --- Final Proximity Check ---
        const actualDiff = Math.abs(actualTs - targetTs);
        // Calculate the maximum allowed difference (handle averageStep=0 case)
        const maxAllowedDiff = this.averageStep > 0 ? FINAL_PROXIMITY_FACTOR * this.averageStep : 0;

        // Check if the found timestamp is too far from the target
        let isTooFar = false;
        if (this.averageStep > 0) {
            isTooFar = actualDiff > maxAllowedDiff;
        } else {
            // If averageStep is 0, require an exact match
            isTooFar = actualDiff !== 0;
        }

        if (isTooFar) {
            // console.log(`Lookup [${method}] result index ${index} (${actualTs}) is too far from target ${targetTs}. Max diff: ${maxAllowedDiff}, Actual diff: ${actualDiff}. Returning null.`);
            // Do not update lastIndex/lastTimestamp, do not log stats for this "failed" lookup
            return null;
        }

        // --- Proximity Check Passed ---

        // Update last known position before logging stats
        this.lastIndex = index;
        this.lastTimestamp = actualTs; // Use the actual timestamp found

        // Log performance stats
        const duration = performance.now() - startPerf;
        this.stats[method].count++;
        this.stats[method].totalTime += duration;
        // console.log(`Lookup [${method}]: ${duration.toFixed(8)} ms -> Index ${index}`); // Optional detailed logging

        // Return the data point
        return this.getDataPoint(index);
    }


    private binarySearchClosest(targetTs: number): number {
        let left = 0;
        let right = this.table.timestamps.length - 1;


        if (targetTs <= this.table.timestamps[left]) {
            return left;
        }
        if (targetTs >= this.table.timestamps[right]) {
            return right;
        }

        let counter = 0; // Counter to track the number of iterations

        while (left <= right) {
            counter++;
            const mid = Math.floor((left + right) / 2);
            const midTs = this.table.timestamps[mid];

            if (midTs === targetTs) {
                // Exact match found
                // console.log(`Binary search found exact match at index ${mid} after ${counter} iterations.`);
                return mid;
            }
        

            if (midTs < targetTs) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }



        const leftDiff = Math.abs(this.table.timestamps[left] - targetTs);
        const rightDiff = Math.abs(this.table.timestamps[right] - targetTs);
        // No exact match, return the closest index
        // console.log(`Binary search (${this.rowCount} rows) found closest match at index ${left} after ${counter} iterations. Left diff: ${leftDiff}, Right diff: ${rightDiff}`);

        return leftDiff < rightDiff ? left : right;
    }


    /**
  * Converts a given index from the dense table into a TimeseriesDataPoint.
  */
    private getDataPoint(index: number): TimeseriesDataPoint {
        const timestamp = this.table.timestamps[index];
        const values: Record<string, number> = {};
        for (const key in this.table.values) {
            values[key] = this.table.values[key][index];
        }
        return { timestamp, values };
    }




    private checkSorting(): boolean {
        for (let i = 0; i < this.rowCount - 1; i++) {
            if (this.table.timestamps[i] > this.table.timestamps[i + 1]) {
                console.error(`Sorting error at index ${i}: ${this.table.timestamps[i]} > ${this.table.timestamps[i + 1]}`);
                return false; // Found an element greater than the next one
            }
        }
        return true; // All elements are sorted
    }


    private checkEvenSpacing(tolerance: number): boolean {
        if (this.rowCount < 3 || this.averageStep === 0) {
            // Need at least 3 points to compare two steps, or if averageStep is 0 (single point or all same time)
            return true;
        }

        // Get the first step
        const firstStep = this.table.timestamps[1] - this.table.timestamps[0];

        // Compare subsequent steps to the first step
        for (let i = 1; i < this.rowCount - 1; i++) {
            const currentStep = this.table.timestamps[i + 1] - this.table.timestamps[i];
            // Check if the absolute difference between the current step and the first step exceeds the tolerance
            // Or check against averageStep if preferred: Math.abs(currentStep - this.averageStep) > tolerance
            if (Math.abs(currentStep - firstStep) > tolerance) {
                console.warn(`Uneven spacing detected at index ${i}: Step=${currentStep}, FirstStep=${firstStep}, Tolerance=${tolerance}`);
                return false; // Found a step difference outside the tolerance
            }
        }
        return true; // All steps are within tolerance
    }

} 