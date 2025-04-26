

export const areArraysSameUnordered = <T>(arr1: T[], arr2: T[]): boolean => {
    if (arr1.length !== arr2.length) {
      return false;
    }
    const set1 = new Set(arr1);
    const set2 = new Set(arr2);
    return !(arr1.some(item => !set2.has(item)) || arr2.some(item => !set1.has(item)));
  }
