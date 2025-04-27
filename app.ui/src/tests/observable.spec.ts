import { describe, it, expect, vi } from 'vitest';
import { Observable } from '../core/observable';

describe('Observable', () => {
  it('should emit the current value immediately upon subscription', () => {
    const observable = new Observable<number>(42);
    const callback = vi.fn();

    observable.subscribe(callback);

    expect(callback).toHaveBeenCalledOnce();
    expect(callback).toHaveBeenCalledWith(42);
  });

  it('should emit new values to all subscribed observers', () => {
    const observable = new Observable<string>();
    const observer1 = vi.fn();
    const observer2 = vi.fn();

    observable.subscribe(observer1);
    observable.subscribe(observer2);

    observable.next('hello');

    expect(observer1).toHaveBeenCalledWith('hello');
    expect(observer2).toHaveBeenCalledWith('hello');
  });

  it('should not call unsubscribed observers', () => {
    const observable = new Observable<boolean>();
    const observer1 = vi.fn();
    const observer2 = vi.fn();

    const subscription1 = observable.subscribe(observer1);
    observable.subscribe(observer2);

    subscription1.unsubscribe();

    observable.next(true);

    expect(observer1).not.toHaveBeenCalled();
    expect(observer2).toHaveBeenCalledWith(true);
  });

  it('should return the latest value with getValue()', () => {
    const observable = new Observable<number>();

    expect(observable.getValue()).toBeUndefined();

    observable.next(10);
    expect(observable.getValue()).toBe(10);
  });
});
