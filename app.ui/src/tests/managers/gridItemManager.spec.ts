import { describe, it, expect, vi, beforeEach } from 'vitest';
import { GridManager, GridManagerItem } from './../../managers/gridItemManager';
import { Observable } from './../../observable';

// Resetting static observables might be needed between tests.
// Here, we assume that the Observable implementation allows us to reassign subscribers.
GridManager.newItemObservable = new Observable<GridManagerItem>();
GridManager.removeItemObservable = new Observable<string>();

describe('GridManager', () => {
    let gm: GridManager;

    beforeEach(() => {
        GridManager.newItemObservable = new Observable<GridManagerItem>();
        GridManager.removeItemObservable = new Observable<string>();
        // Create a new instance for each test so that internal state is clean.
        gm = new GridManager();
    });

    it('should return an empty list of grid items initially', () => {
        expect(gm.getGridItems()).toEqual([]);
    });

    it('should add a new grid item and trigger newItemObservable', () => {
        const newItem = { id: '1', props: { name: 'item1' } };
        const newItemCallback = vi.fn();
        GridManager.newItemObservable.subscribe(newItemCallback);

        gm.addNewItem(newItem);

        expect(gm.getGridItems()).toHaveLength(1);
        expect(gm.getGridItems()[0]).toEqual(newItem);
        expect(newItemCallback).toHaveBeenCalledWith(newItem);
    });

    it('should update an existing item by merging properties', () => {
        const newItem = { id: '1', props: { a: 1 } };
        gm.addNewItem(newItem);

        // Update the item with a new title and an additional property in props
        gm.updateItemById('1', { title: 'Updated', props: { b: 2 } });
        const updated = gm.getItemById('1');

        expect(updated).toEqual({
            id: '1',
            // Merged props: original { a: 1 } plus new { b: 2 }
            props: { a: 1, b: 2 },
            title: 'Updated',
        });
    });

    it('should return undefined for non-existent item', () => {
        expect(gm.getItemById('non-existent')).toBeUndefined();
    });

    it('should remove an item by id and trigger removeItemObservable', () => {
        const newItem = { id: '1', props: { a: 1 } };
        gm.addNewItem(newItem);

        const removeCallback = vi.fn();
        GridManager.removeItemObservable.subscribe(removeCallback);

        gm.removeItemById('1');

        expect(gm.getGridItems()).toHaveLength(0);
        expect(removeCallback).toHaveBeenCalledWith('1');
    });

    it('should remove all items and trigger removeItemObservable for each', () => {
        const newItem1 = { id: '1', props: { a: 1 } };
        const newItem2 = { id: '2', props: { b: 2 } };

        gm.addNewItem(newItem1);
        gm.addNewItem(newItem2);

        const removeCallback = vi.fn();
        GridManager.removeItemObservable.subscribe(removeCallback);

        gm.removeAllItems();

        expect(gm.getGridItems()).toEqual([]);
        expect(removeCallback).toHaveBeenCalledTimes(2);
        expect(removeCallback).toHaveBeenCalledWith('1');
        expect(removeCallback).toHaveBeenCalledWith('2');
    });

    it('should register a new component', () => {
        const compFn = () => 'component';
        gm.registerComponent('comp1', compFn);
        expect(gm.getComponentMap()['comp1']).toEqual(compFn);
    });

    it('should warn when registering a component with an existing key', () => {
        const compFn = () => 'component';
        gm.registerComponent('comp1', compFn);

        const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => { });
        gm.registerComponent('comp1', compFn);
        expect(consoleWarnSpy).toHaveBeenCalledWith('Warning: Component with key "comp1" is already registered.');
        consoleWarnSpy.mockRestore();
    });

    it('should return { x: 0, y: 0 } when no items exist for suggesting free space', () => {
        const space = gm.suggestFreeSpace(2, 2);
        expect(space).toEqual({ x: 0, y: 0 });
    });

    it('should suggest a free space that does not overlap with an existing item', () => {
        // Add an item that occupies space at (0, 0) with width and height of 2
        gm.addNewItem({ id: '1', x: 0, y: 0, w: 2, h: 2, props: {} });
        const space = gm.suggestFreeSpace(2, 2);

        // Validate that the suggested space does not overlap with the occupied item.
        const potentialNewItem = { x: space.x, y: space.y, w: 2, h: 2 };
        const occupiedItem = { x: 0, y: 0, w: 2, h: 2 };

        const isOverlap =
            potentialNewItem.x < occupiedItem.x + occupiedItem.w &&
            potentialNewItem.x + potentialNewItem.w > occupiedItem.x &&
            potentialNewItem.y < occupiedItem.y + occupiedItem.h &&
            potentialNewItem.y + potentialNewItem.h > occupiedItem.y;

        expect(isOverlap).toBe(false);
    });

    it('should log error when adding an item with duplicate id', () => {
        const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => { });
        const newItem = { id: '1', props: { a: 1 } };
        gm.addNewItem(newItem);
        gm.addNewItem(newItem); // attempt to add duplicate
        expect(consoleErrorSpy).toHaveBeenCalledWith('Error: item with id 1 already exists');
        consoleErrorSpy.mockRestore();
    });

    it('should log error when updating a non-existent item', () => {
        const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => { });
        gm.updateItemById('non-existent', { title: 'update', props: { a: 2 } });
        expect(consoleErrorSpy).toHaveBeenCalledWith('Error: item with id non-existent does not exist');
        consoleErrorSpy.mockRestore();
    });

    it('should log error when removing a non-existent item', () => {
        const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => { });
        gm.removeItemById('non-existent');
        expect(consoleErrorSpy).toHaveBeenCalledWith('Error: item with id non-existent does not exist');
        consoleErrorSpy.mockRestore();
    });
});
