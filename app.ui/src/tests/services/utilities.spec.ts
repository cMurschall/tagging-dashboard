import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as utils from '../../services/Tutilities'; // adjust to actual path

// Mocks
vi.mock('../../services/restclient', () => ({
    Configuration: class { },
    ProjectEndpointApi: vi.fn(),
    PlayerEndpointApi: vi.fn(),
    HealthcheckApi: vi.fn(),
}));




// throttle
describe('throttle', () => {
    beforeEach(() => {
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('should call function at most once per limit', () => {
        const fn = vi.fn();
        const throttled = utils.throttle(fn, 1000);
        throttled();
        throttled();
        expect(fn).toHaveBeenCalledTimes(1);
        vi.advanceTimersByTime(1000);
        throttled();
        expect(fn).toHaveBeenCalledTimes(2);
    });
});

// formatWithTemplate
describe('formatWithTemplate', () => {
    it('should format with fixed-point precision', () => {
        const result = utils.formatWithTemplate(12.3456, '{value:F2}');
        expect(result).toBe('12.35');
    });

    it('should format with percent precision', () => {
        const result = utils.formatWithTemplate(0.25, '{value:P1}');
        expect(result).toBe('25.0%');
    });

    it('should fallback on no format specifier', () => {
        const result = utils.formatWithTemplate(42, 'Value is {value} units');
        expect(result).toBe('Value is 42 units');
    });

    it('should handle unsupported format', () => {
        const result = utils.formatWithTemplate(42, '{value:X2}');
        expect(result).toBe('42');
    });
});

// transformMathJsValue
describe('transformMathJsValue', () => {
    it('should evaluate expression using mathjs', () => {
        const result = utils.transformMathJsValue(5, "value + 5");
        expect(result).toBe(10);
    });


    it('should evaluate logarithm using mathjs', () => {
        const result = utils.transformMathJsValue(5, "log10(value)");
        expect(result).toBeCloseTo(0.69897, 2);
    });

    describe('transformMathJsValue Performance', () => {
        const expressions = [
            'value * 2 + 5',
            'sin(value) + cos(value)',
            'sqrt(abs(value^3 - 10)) / (1 + exp(-value))',
            'log(value + 1) * tan(value / 4)'
        ];
        const value = 10;
        const iterations = 10000; // Number of times to call the function
        expressions.forEach((expression) => {
            it(`should show performance improvement with caching after ${iterations} iterations`, async () => {
                // Measure time for the original function
                const startTimeOriginal = performance.now();
                for (let i = 0; i < iterations; i++) {
                    utils.transformMathJsValueNoCompile(value, expression);
                }
                const endTimeOriginal = performance.now();
                const durationOriginal = endTimeOriginal - startTimeOriginal;

                // Measure time for the optimized function
                const startTimeOptimized = performance.now();
                for (let i = 0; i < iterations; i++) {
                    utils.transformMathJsValue(value, expression);
                }
                const endTimeOptimized = performance.now();
                const durationOptimized = endTimeOptimized - startTimeOptimized;

                console.log(`Original function execution time: ${durationOriginal.toFixed(2)} ms`);
                console.log(`Optimized function execution time: ${durationOptimized.toFixed(2)} ms`);

                // Assert that the optimized version is faster (you might need to adjust the threshold)
                expect(durationOptimized).toBeLessThan(durationOriginal * 0.8); // Expect to be at least 20% faster
            });

            it(`should return the same result for both functions: ${expression}`, () => {
                expect(utils.transformMathJsValueNoCompile(value, expression)).toBe(utils.transformMathJsValue(value, expression));
            });

            it('should handle different expressions and values correctly', () => {
                const expression2 = 'sqrt(value)';
                const value2 = 25;
                expect(utils.transformMathJsValueNoCompile(value2, expression2)).toBe(utils.transformMathJsValue(value2, expression2));
            });
        });

    });

});

// areArraysSameUnordered
describe('areArraysSameUnordered', () => {
    it('should return true for same elements in order', () => {
        expect(utils.areArraysSameUnordered([1, 2, 3], [1, 2, 3])).toBe(true);
    });

    it('should return true for same elements in different order', () => {
        expect(utils.areArraysSameUnordered([1, 2, 3], [3, 2, 1])).toBe(true);
    });

    it('should return false for different elements', () => {
        expect(utils.areArraysSameUnordered([1, 2, 3], [4, 5, 6])).toBe(false);
    });

    it('should return false for different lengths', () => {
        expect(utils.areArraysSameUnordered([1, 2], [1, 2, 3])).toBe(false);
    });
});

// isDevMode
describe('isDevMode', () => {
    it('should return true if import.meta.env.MODE is development', () => {
        import.meta.env.MODE = 'development';
        expect(utils.isDevMode()).toBe(true);
    });

    it('should return false if import.meta.env.MODE is production', () => {
        import.meta.env.MODE = 'production';
        expect(utils.isDevMode()).toBe(false);
    });
});
