
import { EmptySubscription, Observable, Subscription } from "../observable";
import { isNotNullOrUndefined, isNullOrUndefined, ShowToastFn, TestDriveProjectInfo, WebSocketBasePath } from "../core/utilities/utilities";
import { DataManager } from "./dataManager";
import { getGridManager, GridManager, GridManagerItem } from './gridItemManager';

import VideoPlayer from './../components/plugins/VideoPlayer.vue';
import ListView from './../components/plugins/ListView.vue';
import Gauge from './../components/plugins/Gauge.vue';
import ScatterPlot from './../components/plugins/ScatterPlot.vue';
import TestGridItem from './../components/plugins/TestGridItem.vue';
import TagTimeline from './../components/plugins/TagTimeline.vue';
import LiveScatterPlot from "../components/plugins/LiveScatterPlot.vue";
import VectorComponentsChart from "../components/plugins/VectorComponentsChart.vue";
import LiveVectorComponentsChart from "../components/plugins/LiveVectorComponentsChart.vue";


import { ApiDataManager } from "./apiDataManager";
import { WebSocketDataConnection } from "../services/webSocketDataConnection";
import { WebsocketDataManager } from "./websocketDataManager";
import { WebSocketSimulationTimeConnection } from "../services/webSocketSimulationTimeConnection";


import { isProxy, toRaw } from "vue";

import { VideoControl } from "../core/videoControl";
import { createVuePluginAdapter } from "../components/pluginContainer";


export interface TaggingDashboardPlugin {
    create: (container: HTMLElement, pluginService: PluginServices) => void;
    onMounted?: () => void;
    onUnmounted?: () => void;
}

export interface PluginServices {
    getId: () => string;

    showMenu$: Observable<boolean>;
    cardTitle$: Observable<string>;

    simulationTime: Observable<number>;
    getProjectInfo: () => TestDriveProjectInfo | undefined;
    getDataManager: () => DataManager,
    showToast: ShowToastFn;
    savePluginState: (state: Record<string, any>) => void;
    getPluginState: () => Record<string, any> | undefined;
    getVideoControl: () => VideoControl;
}

export interface ExternalPluginManifest {
    id: string;
    name: string;
    description: string;
    entry: string; // Path to the main file of the plugin
    version: string;
    defaultSize: { width: number; height: number };
}

export interface InternalPluginManifest {
    name: string;
    displayName: string;
    defaultSize: { width: number; height: number };

}



export class PluginManager {

    private showToast: ShowToastFn = () => '';

    private webSocketDataConnection: WebSocketDataConnection;
    private webSocketSimulationTimeConnection: WebSocketSimulationTimeConnection;

    private gridItemManager: GridManager;

    public readonly simulationTimeObservable = new Observable<number>(0);

    private timeStampSubscription: Subscription = EmptySubscription

    private readonly videoControl = new VideoControl()


    private dataManagers = new Map<string, DataManager>();

    private loadedProject: TestDriveProjectInfo | undefined = undefined;


    private externalPlugins = new Map<string, {
        manifest: ExternalPluginManifest;
        plugin: TaggingDashboardPlugin;
    }>();

    private internalPlugins = new Map<string, {
        manifest: InternalPluginManifest;
    }>([
        ['VideoPlayer', {
            manifest: {
                name: 'VideoPlayer',
                displayName: 'Video Player',
                defaultSize: { width: 6, height: 28 },
            }
        }],
        ['ListView', {
            manifest: {
                name: 'ListView',
                displayName: 'List View',
                defaultSize: { width: 3, height: 20 },
            }
        }],
        ['Gauge', {
            manifest: {
                name: 'Gauge',
                displayName: 'Gauge',
                defaultSize: { width: 3, height: 20 },
            }
        }],
        ['ScatterPlot', {
            manifest: {
                name: 'ScatterPlot',
                displayName: 'Scatter Plot',
                defaultSize: { width: 7, height: 16 },
            }
        }],
        ['TestGridItem', {
            manifest: {
                name: 'TestGridItem',
                displayName: 'Test Grid Item',
                defaultSize: { width: 5, height: 16 },
            }
        }],
        ['TagTimeline', {
            manifest: {
                name: 'TagTimeline',
                displayName: 'Tag Timeline',
                defaultSize: { width: 6, height: 28 },
            }
        }],
        ['VectorComponents', {
            manifest: {
                name: 'VectorComponents',
                displayName: 'Vector Components Chart',
                defaultSize: { width: 7, height: 16 },
            }
        }],
    ])


    // constructor
    public constructor(gridItemManager: GridManager) {
        this.gridItemManager = gridItemManager;

        this.webSocketDataConnection = new WebSocketDataConnection(WebSocketBasePath + '/data');
        this.webSocketSimulationTimeConnection = new WebSocketSimulationTimeConnection(WebSocketBasePath + '/simulationTime');
    }

    public getExternalPlugins(): ExternalPluginManifest[] {
        return Array.from(this.externalPlugins.values()).map((x) => x.manifest);
    }

    public getInternalPlugins(): InternalPluginManifest[] {
        return Array.from(this.internalPlugins.values()).map((x) => x.manifest);
    }

    public setShowToast(showToast: ShowToastFn) {
        this.showToast = showToast;
    }

    public setCurrentProject(project: TestDriveProjectInfo | undefined): void {

        this.timeStampSubscription?.unsubscribe();

        if (isNullOrUndefined(project)) {
            // all data managers back to empty
            this.dataManagers.clear();

            this.loadedProject = undefined;

            // clear all plugins
            this.gridItemManager.removeAllItems();
            return;
        }

        this.registerComponents(project);

        const isLiveProject = project.isLive
        if (isLiveProject) {
            // unsubscribe from old data connection todo!!
            this.timeStampSubscription = this.webSocketDataConnection.data$.subscribe((data) => {
                // in a live project we have to set the internal simulation clock  to the current time
                // every time we receive a new data point
                this.simulationTimeObservable.next(data.timestamp);
            });
        }
        else {
            this.timeStampSubscription = this.simulationTimeObservable.subscribe((time) => {
                // if we have a non live project we can set the time to an arbitrary value.
                // so we need to inform the simulation time connection about the current time
                this.webSocketSimulationTimeConnection.sendCurrentTimeStamp(time);
            });
        }

        this.loadedProject = project;
    }


    public restorePlugin(plugin: GridManagerItem, pluginState: Record<string, any> | undefined): void {

        const service = this.getCurrentService(plugin.id);

        if (isNotNullOrUndefined(pluginState)) {
            service.getPluginState = () => pluginState;
        }
        // preserve and merge the dependencies
        plugin.dependencies = {
            pluginService: service
        };

        this.gridItemManager.addNewItem(plugin);
    }


    public showPlugin(pluginName: string, props: Record<string, any>): void {
        let id: string;
        if (pluginName === 'VideoPlayer' || pluginName === 'TagTimeline') {
            id = pluginName;
        } else {
            id = pluginName + '_' + crypto.randomUUID();
        }

        const isInternalPlugin = this.internalPlugins.has(pluginName);
        if (!isInternalPlugin && !this.externalPlugins.has(pluginName)) {
            console.warn(`Plugin ${pluginName} is not registered`);
            return;
        }

        const service = this.getCurrentService(id);
        const size = isInternalPlugin
            ? this.internalPlugins.get(pluginName)?.manifest.defaultSize
            : this.externalPlugins.get(pluginName)?.manifest.defaultSize;

        const newItem = {
            id: id,
            // spread x and y from the gridItemManager (does not really work well yet)
            //...this.gridItemManager.suggestFreeSpace(this.pluginSizes[pluginName].w, this.pluginSizes[pluginName].h),
            w: size?.width,
            h: size?.height,
            component: pluginName,
            title: pluginName,
            props: props,
            dependencies: {
                pluginService: service
            }
        };

        this.gridItemManager.addNewItem(newItem);
    }


    public async loadExternalPlugins(): Promise<void> {
        try {
            const response = await fetch('/plugins/plugin-index.json');
            const pluginDirs: string[] = await response.json();

            for (const dir of pluginDirs) {
                try {
                    const manifestUrl = `/plugins/${dir}/manifest.json`;
                    const manifest = await fetch(manifestUrl).then(res => res.json());
                    // console.log(manifest);

                    // import the plugin module dynamically
                    const pluginModule = await import(/* @vite-ignore */ `/plugins/${dir}/${manifest.entry}`);


                    // Check if the module has a default export
                    if (pluginModule?.default) {
                        //this.externalPlugins.set(manifest, pluginModule.default);

                        this.externalPlugins.set(manifest.id, {
                            manifest,
                            plugin: pluginModule.default
                        });

                        console.log(`Loaded external plugin: ${manifest.id}`);
                    } else {
                        console.warn(`Plugin ${dir} has no default export`);
                    }
                } catch (err) {
                    console.error(`Failed to load external plugin '${dir}':`, err);
                }
            }
        } catch (error) {
            console.error('Failed to load external plugins:', error);
        }
    }


    private registerComponents(project: TestDriveProjectInfo) {

        this.gridItemManager.unregisterAllComponents();
        this.gridItemManager.registerComponent('ListView', () => createVuePluginAdapter(ListView));
        this.gridItemManager.registerComponent('VideoPlayer', () => createVuePluginAdapter(VideoPlayer));
        this.gridItemManager.registerComponent('Gauge', () => createVuePluginAdapter(Gauge));
        this.gridItemManager.registerComponent('ScatterPlot', () => project.isLive ? createVuePluginAdapter(LiveScatterPlot) : createVuePluginAdapter(ScatterPlot));
        this.gridItemManager.registerComponent('TestGridItem', () => createVuePluginAdapter(TestGridItem));
        this.gridItemManager.registerComponent('TagTimeline', () => createVuePluginAdapter(TagTimeline));
        this.gridItemManager.registerComponent('VectorComponents', () => project.isLive ?  createVuePluginAdapter(LiveVectorComponentsChart) : createVuePluginAdapter(VectorComponentsChart));

        for (const [id, external] of this.externalPlugins) {
            this.gridItemManager.registerComponent(id, () => external.plugin);
        }
    }


    private getCurrentService(pluginId: string): PluginServices {

        let dataManager = this.dataManagers.get(pluginId);
        if (!dataManager) {
            dataManager = this.loadedProject?.isLive
                ? new WebsocketDataManager(this.webSocketDataConnection)
                : new ApiDataManager();

            dataManager.subscribeToTimestamp(this.simulationTimeObservable);
            this.dataManagers.set(pluginId, dataManager);
        }

        const showMenu$ = new Observable<boolean>(false);
        const cardTitle$ = new Observable<string>("");


        return {
            getId: () => pluginId,

            showMenu$: showMenu$,
            cardTitle$: cardTitle$,

            simulationTime: this.simulationTimeObservable,
            getProjectInfo: () => this.loadedProject,
            getDataManager: () => {
                if (!dataManager) throw new Error(`No dataManager found for pluginId=${pluginId}`);
                return dataManager;
            },
            showToast: this.showToast,
            savePluginState: (state: Record<string, any>) => {
                const item = this.gridItemManager.getGridItems().find(i => i.id === pluginId);
                if (!item) {
                    console.warn(`Plugin state update failed: no item found with id '${pluginId}'`);
                    return;
                }

                const rawState = isProxy(state) ? toRaw(state) : state;
                this.gridItemManager.updateItemById(pluginId, {
                    pluginState: { ...JSON.parse(JSON.stringify(rawState)) },
                });
            },
            getPluginState: () => {
                const item = this.gridItemManager.getGridItems().find(i => i.id === pluginId);
                if (!item) {
                    console.warn(`Plugin state retrieval failed: no item found with id '${pluginId}'`);
                    return undefined;
                }
                return item.pluginState;
            },
            getVideoControl: () => this.videoControl,
        };
    }
}


// Export a function to get the singleton instance
let instance: PluginManager | undefined;

export const getPluginManager = (): PluginManager => {
    if (!instance) {
        instance = new PluginManager(getGridManager());
    }
    return instance;
}