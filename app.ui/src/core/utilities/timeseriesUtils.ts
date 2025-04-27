import { TimeseriesDataPoint, TimeseriesTable, TimestampStatistics } from "@/types/data";







// Helper function to convert an array of TimeseriesDataPoint into a TimeseriesTable.
export const toDenseTable = (dataPoints: TimeseriesDataPoint[]): TimeseriesTable => {
    const timestamps = new Float64Array(dataPoints.map((dp) => dp.timestamp));
    const values: Record<string, number[]> = {};
    for (const dp of dataPoints) {
        for (const key in dp.values) {
            if (!values[key]) {
                values[key] = [];
            }
            if (typeof dp.values[key] === 'number') {
                values[key].push(dp.values[key]);
            }
            if (Array.isArray(dp.values[key])) {
                values[key].push(...dp.values[key]);
            }
        }
    }
    const denseValues: Record<string, Float64Array> = {};
    for (const key in values) {
        denseValues[key] = new Float64Array(values[key]);
    }
    return { timestamps, scalarValues: denseValues, vectorValues: {} };
}






export const getTimestampStatistics = (table: TimeseriesTable): TimestampStatistics => {
    const ts = table.timestamps;
    const count = ts.length;

    if (count < 2) {
        return {
            count,
            min: ts[0] ?? NaN,
            max: ts[0] ?? NaN,
            duration: 0,
            meanInterval: 0,
            medianInterval: 0,
            minInterval: 0,
            maxInterval: 0,
            uniform: true
        };
    }

    const min = ts[0];
    const max = ts[ts.length - 1];
    const duration = max - min;

    const intervals: number[] = [];
    for (let i = 1; i < ts.length; i++) {
        intervals.push(ts[i] - ts[i - 1]);
    }

    const meanInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;

    const sortedIntervals = [...intervals].sort((a, b) => a - b);
    const mid = Math.floor(sortedIntervals.length / 2);
    const medianInterval = sortedIntervals.length % 2 === 0
        ? (sortedIntervals[mid - 1] + sortedIntervals[mid]) / 2
        : sortedIntervals[mid];

    const minInterval = sortedIntervals[0];
    const maxInterval = sortedIntervals[sortedIntervals.length - 1];

    const tolerance = 1e-9;
    const uniform = maxInterval - minInterval < tolerance;

    return {
        count,
        min,
        max,
        duration,
        meanInterval,
        medianInterval,
        minInterval,
        maxInterval,
        uniform
    };
}