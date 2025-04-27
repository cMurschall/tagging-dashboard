import { Observable } from "@/core/observable";
import { TestDriveProjectInfo } from "@/core/utilities/utilities";
import { VideoControl } from "@/core/videoControl";
import { DataManager } from "@/managers/dataManager";
import { ShowToastFn } from "./grid";

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