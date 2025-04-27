import { Subscription } from "@/types/observable";


export class Observable<T> {
  private observers: ((value: T) => void)[] = [];
  private currentValue: T | undefined;

  constructor(initialValue?: T) {
    this.currentValue = initialValue;
  }

  subscribe(observer: (value: T) => void): Subscription {
    this.observers.push(observer);

    // Immediately emit the current value if it exists
    if (this.currentValue !== undefined) {
      observer(this.currentValue);
    }

    return {
      unsubscribe: () => {
        this.observers = this.observers.filter((o) => o !== observer);
      },
    };
  }

  next(value: T): void {
    this.currentValue = value;
    this.observers.forEach((observer) => observer(value));
  }

  getValue(): T | undefined {
    return this.currentValue;
  }
}

