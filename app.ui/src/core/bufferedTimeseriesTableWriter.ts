import { TimeseriesDataPoint, TimeseriesTable } from "@/types/data";


export class BufferedTimeseriesTableWriter {
  private buffer: TimeseriesDataPoint[] = [];
  private lastFlushTime = Date.now();
  private flushInterval = 10000; // 10 seconds
  private flushCount = 100;

  constructor(private table: TimeseriesTable) {
    // Start periodic timer
    setInterval(() => this.flushIfNeeded(), 1000);
  }

  add(point: TimeseriesDataPoint) {
    this.buffer.push(point);
    this.flushIfNeeded();
  }

  private flushIfNeeded() {
    const now = Date.now();
    const timeElapsed = now - this.lastFlushTime;

    if (this.buffer.length >= this.flushCount || timeElapsed >= this.flushInterval) {
      this.flush();
    }
  }

  private flush() {
    if (this.buffer.length === 0) return;

    const n = this.buffer.length;
    const existingLength = this.table.timestamps.length;

    // --- Timestamps ---
    const newTimestamps = new Float64Array(existingLength + n);
    newTimestamps.set(this.table.timestamps);
    for (let i = 0; i < n; i++) {
      newTimestamps[existingLength + i] = this.buffer[i].timestamp;
    }
    this.table.timestamps = newTimestamps;

    // --- Data Points ---
    for (const point of this.buffer) {
      for (const [key, value] of Object.entries(point.values)) {
        if (typeof value === 'number') {
          // Scalar value
          const oldArr = this.table.scalarValues[key] ?? new Float64Array(existingLength);
          const newArr = new Float64Array(oldArr.length + 1);
          newArr.set(oldArr);
          newArr[oldArr.length] = value;
          this.table.scalarValues[key] = newArr;
        }
        if (Array.isArray(value)) {
          // Vector value
          const dims = value.length;

          // Initialize vector arrays if not present
          if (!this.table.vectorValues[key]) {
            this.table.vectorValues[key] = Array.from({ length: dims }, () => new Float64Array(existingLength)
            );
          }

          for (let d = 0; d < dims; d++) {
            const oldVec = this.table.vectorValues[key][d];
            const newVec = new Float64Array(oldVec.length + 1);
            newVec.set(oldVec);
            newVec[oldVec.length] = value[d];
            this.table.vectorValues[key][d] = newVec;
          }
        }
      }
    }

    this.buffer = [];
    this.lastFlushTime = Date.now();
  }
}
