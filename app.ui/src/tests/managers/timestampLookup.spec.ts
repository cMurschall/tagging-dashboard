import { describe, it, expect } from 'vitest';
import { TimestampLookup } from '../../services/timestampLookup';
import { TimeseriesDataPoint, TimeseriesTable } from '../../managers/dataManager';
import { toDenseTable } from '../../services/utilities';



describe('TimestampLookup', () => {
  const dataPoints: TimeseriesDataPoint[] = [
    { timestamp: 1000, values: { a: 1 } },
    { timestamp: 2000, values: { a: 2 } },
    { timestamp: 3000, values: { a: 3 } },
    { timestamp: 4000, values: { a: 4 } },
    { timestamp: 5000, values: { a: 5 } },
  ];
  const table = toDenseTable(dataPoints);

  it('should return null if the table is empty', () => {
    const emptyTable: TimeseriesTable = { timestamps: new Float64Array([]), values: {} };
    const lookup = new TimestampLookup(emptyTable);
    expect(lookup.lookup(1500)).toBeNull();
  });

  it('should return the only element for a single-element table (binary search fallback)', () => {
    const singleData: TimeseriesDataPoint[] = [{ timestamp: 1000, values: { a: 1 } }];
    const singleTable = toDenseTable(singleData);
    const lookup = new TimestampLookup(singleTable);
    expect(lookup.lookup(500)).toEqual(singleData[0]);
    expect(lookup.lookup(1500)).toEqual(singleData[0]);
  });

  it('should return the closest data point using forward scanning', () => {
    const lookup = new TimestampLookup(table);
    // Initial state: lastTimestamp = 1000.
    // Lookup 1500: forward scan should run because 1500 - 1000 = 500 is within the max scan delta.
    // Between 1000 and 2000, both are equally distant (500), so the algorithm picks the first (timestamp 1000).
    const result1 = lookup.lookup(1500);
    expect(result1).toEqual(dataPoints[0]);

    // Lookup 2500: starting from the previous state, forward scan should advance to the element with timestamp 2000.
    const result2 = lookup.lookup(2500);
    expect(result2).toEqual(dataPoints[1]);

    // Lookup exact timestamp: 3000 should return the element with timestamp 3000.
    const result3 = lookup.lookup(3000);
    expect(result3).toEqual(dataPoints[2]);
  });

  it('should return the closest data point using reverse scanning', () => {
    const lookup = new TimestampLookup(table);
    // First, do a forward lookup to update the state.
    const initialResult = lookup.lookup(3500); // Expected to return the element at timestamp 3000.
    expect(initialResult).toEqual(dataPoints[2]);
    // Now, perform a reverse lookup with a target slightly less than the current state.
    const result = lookup.lookup(3200);
    // With lastTimestamp = 3500 and starting index at the element with timestamp 3000,
    // the reverse scan should keep the index at 2 (timestamp 3000) since it's closer.
    expect(result).toEqual(dataPoints[2]);
  });

  it('should return the closest data point using interpolation guess', () => {
    const lookup = new TimestampLookup(table);
    // With timestamps from 1000 to 5000, the average step is 1000.
    // For a target like 8000, the forward/reverse conditions are not met and the interpolation branch is used.
    const result = lookup.lookup(8000);
    // The closest element is at timestamp 5000.
    expect(result).toEqual(dataPoints[4]);
  });

  it('should correctly return the closest index using binarySearchClosest', () => {
    const lookup = new TimestampLookup(table);
    // Access the private binarySearchClosest via bracket notation.
    const binarySearchClosest = (lookup as any)['binarySearchClosest'].bind(lookup);
    // For 1500, the closest should be index 0 (difference of 500 with dataPoints[0] and dataPoints[1]).
    expect(binarySearchClosest(1500)).toBe(0);
    // For 2500, the closest should be index 1.
    expect(binarySearchClosest(2500)).toBe(1);
    // For 3500, the closest should be index 2.
    expect(binarySearchClosest(3500)).toBe(2);
    // For 4500, the closest should be index 3.
    expect(binarySearchClosest(4500)).toBe(3);
  });

  it('should perform well on a large table', () => {
    // Create a large table with 1,000,000 data points.
    const count = 1_000_000;
    const startTime = 1_000; // arbitrary start time
    const step = 10; // each timestamp is 10 ms apart
    const data: TimeseriesDataPoint[] = [];
    for (let i = 0; i < count; i++) {
      data.push({
        timestamp: startTime + i * step,
        values: { a: i },
      });
    }
    const largeTable = toDenseTable(data);
    const lookup = new TimestampLookup(largeTable);
    const numLookups = 10;
    const lookupTimes: number[] = [];
    const randomTimestamps: number[] = [];
    const tableStart = data[0].timestamp;
    const tableEnd = data[data.length - 1].timestamp;
    for (let i = 0; i < numLookups; i++) {
      const randomTimestamp = tableStart + Math.floor(Math.random() * (tableEnd - tableStart));
      randomTimestamps.push(randomTimestamp);
    }
    for (const ts of randomTimestamps) {
      const start = performance.now();
      const result = lookup.lookup(ts);
      const end = performance.now();
      lookupTimes.push(end - start);
      expect(result).not.toBeNull();
    }
    const totalTime = lookupTimes.reduce((sum, t) => sum + t, 0);
    const avgTime = totalTime / numLookups;
    console.log(`Average lookup time over ${numLookups} calls: ${avgTime.toFixed(4)} ms`);
    expect(avgTime).toBeLessThan(0.1);
  });
});
