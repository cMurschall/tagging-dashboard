
import { Observable } from "../observable";
import { TestDriveProjectInfo } from "../services/utilities";
import { DataManager, EmptyDataManager } from "./dataManager";
import gridManager, { GridManager } from './gridItemManager';

import VideoPlayer from './../components/plugins/VideoPlayer.vue';
import ListView from './../components/plugins/ListView.vue';
import Gauge from './../components/plugins/Gauge.vue';
import ScatterPlot from './../components/plugins/ScatterPlot.vue';
import TestGridItem from './../components/plugins/TestGridItem.vue';
import TagTimeline from './../components/plugins/TagTimeline.vue';
import { ApiDataManager } from "./apiDataManager";


export interface PluginServices {
    simulationTime: Observable<number>;
    getProjectInfo: () => TestDriveProjectInfo | undefined;
    getDataManager: () => DataManager

}

export type PluginType = 'ListView' | 'VideoPlayer' | 'Gauge' | 'ScatterPlot' | 'TestGridItem' | 'TagTimeline';



export class PluginManager {

    private gridItemManager: GridManager;

    public readonly simulationTimeObservable = new Observable<number>(0);

    private pluginSizes = {
        ListView: { w: 3, h: 5 },
        VideoPlayer: { w: 6, h: 7 },
        Gauge: { w: 3, h: 5 },
        ScatterPlot: { w: 7, h: 4 },
        TestGridItem: { w: 5, h: 4 },
        TagTimeline: { w: 6, h: 7 },
    } as Record<PluginType, { w: number; h: number }>;

    private dataManagers = {
        ListView: new EmptyDataManager(),
        VideoPlayer: new EmptyDataManager(),
        Gauge: new EmptyDataManager(),
        ScatterPlot: new EmptyDataManager(),
        TestGridItem: new EmptyDataManager(),
        TagTimeline: new EmptyDataManager(),
    } as Record<PluginType, EmptyDataManager>;


    private loadedProject: TestDriveProjectInfo | undefined = undefined;


    // constructor
    public constructor(gridItemManager: GridManager) {
        this.gridItemManager = gridItemManager;

        this.registerComponents();
    }




    public setCurrentProject(project: TestDriveProjectInfo | undefined): void {
        if (!project) {
            // all data managers back to empty
            for (const key in this.dataManagers) {
                this.dataManagers[key as PluginType] = new EmptyDataManager();
            }
        }

        // for now we only support the api data manager
        for (const key in this.dataManagers) {
            const dataManager = new ApiDataManager();
            dataManager.subscribeToTimestamp(this.simulationTimeObservable);
            this.dataManagers[key as PluginType] = dataManager;
        }

        this.loadedProject = project;
    }



    private registerComponents() {
        this.gridItemManager.setComponentMap({
            ListView: () => (ListView),
            VideoPlayer: () => (VideoPlayer),
            Gauge: () => (Gauge),
            ScatterPlot: () => (ScatterPlot),
            TestGridItem: () => (TestGridItem),
            TagTimeline: () => (TagTimeline),
        });
    }


    public showPlugin(pluginName: PluginType): void {

        const service = {
            simulationTime: this.simulationTimeObservable,
            getProjectInfo: (): TestDriveProjectInfo | undefined => this.loadedProject,
            getDataManager: () => this.dataManagers[pluginName]
        };

        const newItem = {
            id: pluginName + '_' + crypto.randomUUID(),
            // spread x and y from the gridItemManager
            ...this.gridItemManager.suggestFreeSpace(this.pluginSizes[pluginName].w, this.pluginSizes[pluginName].h),
            w: this.pluginSizes[pluginName].w,
            h: this.pluginSizes[pluginName].h,
            component: pluginName,
            title: pluginName,
            props: {},
            dependencies: {
                pluginService: service
            }
        };

        switch (pluginName) {
            case 'VideoPlayer':
                // only one video player is allowed
                newItem.id = 'VideoPlayer';
                break;
            case 'TagTimeline':
                // only one tag timeline is allowed
                newItem.id = 'TagTimeline';
                break;
            default:
                break;

        }

        this.gridItemManager.addNewItem(newItem);
    }


}


const pluginManager = new PluginManager(gridManager);
// Export a function to get the singleton instance
export default pluginManager;