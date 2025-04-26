import * as math from 'mathjs'


export const IDENTITY_EXPRESSION = 'value';



// const compiledExpressions: { [expression: string]: math.EvalFunction } = {};
const compiledExpressions = new Map<string, math.EvalFunction>();
export const transformMathJsValue = (value: number, expression: string): number => {
    if (!expression || expression.trim() === IDENTITY_EXPRESSION) {
        return value;
    }
    try {
        // Check if the expression has already been compiled
        if (!compiledExpressions.has(expression)) {
            // Compile the expression and store it
            compiledExpressions.set(expression, math.compile(expression));
        }

        // Retrieve the compiled expression
        const compiledExpression = compiledExpressions.get(expression)!;

        // Evaluate the compiled expression with the scope
        const scope = { value };
        const evaluated = compiledExpression.evaluate(scope);

        return evaluated as number;
    } catch (error) {
        console.error('Error evaluating expression:', error);
        return value; // Return original value on error
    }
};

export const transformMathJsValueNoCompile = (value: number, expression: string): number => {
    try {
        const scope = { value };
        const evaluated = math.evaluate(expression, scope);
        return evaluated as number;
    } catch (error) {
        console.error('Error evaluating expression:', error);
        return value; // Return original value on error
    }
};




const formatRegExp = new RegExp(`\\{${IDENTITY_EXPRESSION}(?::([A-Za-z]\\d*))?\\}`);
export const formatWithTemplate = (value: number, formatTemplate: string): string => {
    if (!formatTemplate || formatTemplate.trim() === IDENTITY_EXPRESSION) {
        return String(value);
    }
    // Match against the template
    const match = formatTemplate.match(formatRegExp);

    // Replace fallback, using the same constant again
    if (!match) {
        return formatTemplate.replace(`{${IDENTITY_EXPRESSION}}`, String(value));
    }

    const formatSpecifier = match[1];
    let numberFormatOptions = {};

    if (formatSpecifier) {
        const formatType = formatSpecifier.charAt(0).toUpperCase();
        const precision = parseInt(formatSpecifier.slice(1), 10);

        switch (formatType) {
            case 'F': // Fixed-point
                numberFormatOptions = {
                    style: 'decimal',
                    minimumFractionDigits: isNaN(precision) ? 2 : precision,
                    maximumFractionDigits: isNaN(precision) ? 2 : precision,
                };
                break;
            case 'P': // Percent
                numberFormatOptions = {
                    style: 'percent',
                    minimumFractionDigits: isNaN(precision) ? 0 : precision,
                    maximumFractionDigits: isNaN(precision) ? 0 : precision,
                };
                break;
            case 'N':
                numberFormatOptions = {
                    style: 'decimal',
                    useGrouping: true,
                    minimumFractionDigits: isNaN(precision) ? 0 : precision,
                    maximumFractionDigits: isNaN(precision) ? 0 : precision,
                };
                break;
            case 'E':
                const expPrecision = isNaN(precision) ? 2 : precision;
                const exponentialValue = value.toExponential(expPrecision);
                return formatTemplate.replace(match[0], exponentialValue);

            default:
                console.warn(`Unsupported format specifier: ${formatSpecifier}`);
        }
    }

    try {
        const formatter = new Intl.NumberFormat('en-US', numberFormatOptions);
        const formattedValue = formatter.format(value);
        return formatTemplate.replace(match[0], formattedValue);
    } catch (error) {
        console.error("Error formatting number:", error);
        return formatTemplate.replace(match[0], String(value));
    }
}



export const throttle = <T extends (...args: any[]) => void>(func: T, limit: number): T => {
    let lastCall = 0;
    return function (this: any, ...args: any[]) {
        const now = Date.now();
        if (now - lastCall >= limit) {
            lastCall = now;
            func.apply(this, args);
        }
    } as T;
}



export const clamp = (val: number, min: number, max: number) => Math.min(Math.max(val, min), max)


