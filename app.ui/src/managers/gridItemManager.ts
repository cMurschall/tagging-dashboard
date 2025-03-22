import { Observable } from "../observable";


export interface GridItem<T = Record<string, any>> {
    id: string;
    x?: number;
    y?: number;
    w?: number;
    h?: number;
    component?: string;
    title?: string;
    props?: T;
    dependencies?: Record<string, any> | undefined;
}

let gridItems: GridItem[] = [];
let componentMap: Record<string, () => any> = {};

export const newItemObservable = new Observable<GridItem>();
export const removeItemObservable = new Observable<string>();


export function getGridItems(): GridItem[] {
    return gridItems;
}

export function getComponentMap(): Record<string, () => any> {
    return componentMap;
}

export function setComponentMap(map: Record<string, () => any>): void {
    componentMap = map;
}

export function registerComponent(key: string, componentFactory: () => any): void {
    if (componentMap[key]) {
        console.warn(`Warning: Component with key "${key}" is already registered.`);
    }
    componentMap[key] = componentFactory;
}

export function addNewItem<T extends Record<string, any>>(item: Omit<GridItem<T>, 'props'> & { props: T }): void {
    if (gridItems.find((i) => i.id === item.id)) {
        console.error(`Error: item with id ${item.id} already exists`);
        return;
    }

    if (item.dependencies) {
        item.dependencies = (item.dependencies);
    }

    gridItems.push(item);
    newItemObservable.next(item);
}

export function removeItemById(id: string): void {
    const index = gridItems.findIndex((i) => i.id === id);
    if (index === -1) {
        console.error(`Error: item with id ${id} does not exist`);
        return;
    }

    const removedItem = gridItems.splice(index, 1)[0];
    removeItemObservable.next(removedItem.id);
}

export function removeAllItems(): void {
    const items = [...gridItems];
    gridItems = [];
    items.forEach((item) => removeItemObservable.next(item.id));
}