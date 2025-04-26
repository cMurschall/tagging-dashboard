export const isNotNullOrUndefined = <T>(val: T | null | undefined): val is T => { return val !== null && val !== undefined }

export const isNullOrUndefined = (val: unknown): val is null | undefined => { return val === null || val === undefined }

