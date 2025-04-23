import { Observable } from "../observable";

export interface GridManagerItem {
    id: string;
    x?: number;
    y?: number;
    w?: number;
    h?: number;
    component?: string;
    title?: string;
    props?: Record<string, any> | undefined;
    pluginState?: Record<string, any> | undefined;
    dependencies?: Record<string, any> | undefined;
}

export class GridManager {
    private GridManagerItems: GridManagerItem[] = [];
    private componentMap: Record<string, () => any> = {};

    public static newItemObservable = new Observable<GridManagerItem>();
    public static removeItemObservable = new Observable<string>();

    public getGridItems(): GridManagerItem[] {
        return this.GridManagerItems;
    }

    public getComponentMap(): Record<string, () => any> {
        return this.componentMap;
    }

    public setComponentMap(map: Record<string, () => any>): void {
        this.componentMap = map;
    }

    public registerComponent(key: string, componentFactory: () => any): void {
        if (this.componentMap[key]) {
            console.warn(`Warning: Component with key "${key}" is already registered.`);
        }
        this.componentMap[key] = componentFactory;
    }

    public addNewItem(item: GridManagerItem): void {
        if (this.GridManagerItems.find((i) => i.id === item.id)) {
            console.error(`Error: item with id ${item.id} already exists`);
            return;
        }

        if (item.dependencies) {
            item.dependencies = (item.dependencies);
        }

        this.GridManagerItems.push(item);
        GridManager.newItemObservable.next(item);
    }

    public updateItemById(id: string, item: Partial<Omit<GridManagerItem, 'props'>> & { props?: Partial<GridManagerItem['props']> }): void {
        const index = this.GridManagerItems.findIndex((i) => i.id === id);
        if (index === -1) {
            console.error(`Error: item with id ${id} does not exist`);
            return;
        }
        const existingItem = this.GridManagerItems[index];

        // Merge the existing item with the new properties
        this.GridManagerItems[index] = {
            ...existingItem,
            ...item,
            props: { ...existingItem.props, ...item.props },
        };
    }

    public getItemById(id: string): GridManagerItem | undefined {
        return this.GridManagerItems.find((item) => item.id === id);
    }

    public removeItemById(id: string): void {
        const index = this.GridManagerItems.findIndex((i) => i.id === id);
        if (index === -1) {
            console.error(`Error: item with id ${id} does not exist`);
            return;
        }

        const removedItem = this.GridManagerItems.splice(index, 1)[0];
        GridManager.removeItemObservable.next(removedItem.id);
    }

    public removeAllItems(): void {
        const items = [...this.GridManagerItems];
        this.GridManagerItems = [];
        items.forEach((item) => GridManager.removeItemObservable.next(item.id));
    }

    public suggestFreeSpace(width: number, height: number): { x: number; y: number } {
        if (width <= 0 || height <= 0) {
            console.warn("Warning: Width and height must be positive values.");
            return { x: 0, y: 0 };
        }

        const occupiedSpaces = this.GridManagerItems.filter(
            item => item.x !== undefined && item.y !== undefined && item.w !== undefined && item.h !== undefined
        ) as Required<GridManagerItem>[];

        // If empty, suggest top-left
        if (occupiedSpaces.length === 0) {
            return { x: 0, y: 0 };
        }

        let maxX = 0;
        let maxY = 0;
        for (const item of occupiedSpaces) {
            maxX = Math.max(maxX, item.x + item.w);
            maxY = Math.max(maxY, item.y + item.h);
        }

        const searchWidth = maxX + width + 1;
        const searchHeight = maxY + height + 1;
        const centerX = Math.floor(searchWidth / 2);
        const centerY = Math.floor(searchHeight / 2);

        // Generate all candidate positions
        const candidates: { x: number; y: number; dist: number }[] = [];
        for (let x = 0; x < searchWidth; x++) {
            for (let y = 0; y < searchHeight; y++) {
                const dist = Math.sqrt((x - centerX) ** 2 + (y - centerY) ** 2);
                candidates.push({ x, y, dist });
            }
        }

        // Sort by distance to center (closest first)
        candidates.sort((a, b) => a.dist - b.dist);

        // Check candidates
        for (const { x, y } of candidates) {
            const potentialNewItem = { x, y, w: width, h: height };
            let isOverlap = false;

            for (const occupiedItem of occupiedSpaces) {
                if (
                    potentialNewItem.x < occupiedItem.x + occupiedItem.w &&
                    potentialNewItem.x + potentialNewItem.w > occupiedItem.x &&
                    potentialNewItem.y < occupiedItem.y + occupiedItem.h &&
                    potentialNewItem.y + potentialNewItem.h > occupiedItem.y
                ) {
                    isOverlap = true;
                    break;
                }
            }

            if (!isOverlap) {
                return { x, y };
            }
        }

        // Fallback
        return { x: 0, y: 0 };
    }
}

let instance: GridManager | undefined;

export const getGridManager = (): GridManager => {
    if (!instance) {
        instance = new GridManager();
    }
    return instance;
}
