<template>

    <div>
        <Transition name="fade" mode="out-in">
            <div v-if="showMenu">
                <BRow class="mb-2">
                    <BCol cols="12">
                        <h4>List Options</h4>
                    </BCol>
                </BRow>
                <BRow>
                    <BCol cols="12">
                        <BButton @click="handleAddRow" variant="primary">Add New Row</BButton>

                    </BCol>
                </BRow>



                <div class="mb-3 border p-2">
                    <BRow>
                        <BCol cols="4">
                            <label class="small">Data column:</label>
                        </BCol>
                        <BCol cols="3">
                            <label class="small">Detail formatter:</label>
                        </BCol>
                        <BCol cols="3">
                            <label class="small">Math js converter:</label>
                        </BCol>
                        <BCol cols="1"></BCol>
                    </BRow>
                    <BRow v-for="(_, index) in pluginState.columnDataInfos" :key="index" class="mb-2">
                        <BCol cols="4">
                            <!-- <label for="input-data-column"  class="small">Data column:</label> -->
                            <!-- <BFormSelect size="sm" v-model="pluginState.columnDataInfos[index].selectedColumn"
                                :options="availableColumns">
                                <template #first>
                                    <BFormSelectOption :value="null" disabled>-- Please select an option --
                                    </BFormSelectOption>
                                </template>
</BFormSelect> -->

                            <FilterableSelect v-model="pluginState.columnDataInfos[index].selectedColumn"
                                :options="availableColumns" :getLabel="(item: ColumnInfo) => item.name"
                                placeholder="Select Columns:" />
                        </BCol>


                        <BCol cols="3">

                            <!-- <label for="input-value-format"  class="small">Value format:</label> -->
                            <BFormInput v-model="pluginState.columnDataInfos[index].valueFormat"
                                placeholder="Detail formatter:" size="sm" style="font-family: monospace ;"></BFormInput>

                        </BCol>
                        <BCol cols="3">
                            <!-- <label for="input-value-converter"  class="small">Value converter:</label> -->
                            <BFormInput v-model="pluginState.columnDataInfos[index].valueConverter"
                                placeholder="Math js converter:" size="sm" style="font-family: monospace ;">
                            </BFormInput>

                        </BCol>

                        <BCol cols="1">
                            <BButton @click="handleRemoveRow(index)" variant="danger" size="sm">
                                X
                            </BButton>

                        </BCol>
                    </BRow>
                </div>



            </div>
        </Transition>
        <div>
            <BTableSimple small caption-top responsive striped bordered class="data-list-table">
                <template #caption>
                    <h4>Data List</h4>
                </template>
                <BThead>
                    <BTr>
                        <BTh class="column-header">Column</BTh>
                        <BTh class="value-header">Value</BTh>
                    </BTr>
                </BThead>
                <BTbody v-if="pluginState.columnDataInfos.length > 0">

                    <BTr>
                        <BTd class="column-cell">Time</BTd>
                        <BTd class="value-cell">{{ displayData.timestamp }}</BTd>
                    </BTr>

                    <BTr v-for="(value, index) in pluginState.columnDataInfos" :key="index">

                        <BTd class="column-cell">{{ value.selectedColumn?.name }}</BTd>
                        <!-- <BTd class="value-cell">{{ formatValue(value, key) }}</BTd> -->
                        <BTd class="value-cell">{{ showValue(value.selectedColumn?.name) }}</BTd>
                    </BTr>
                </BTbody>

                <template #empty>No data available</template>

            </BTableSimple>
        </div>
    </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, inject, watch, toRaw } from 'vue';
import { TimeseriesDataPoint } from '../../managers/dataManager';
import { EmptySubscription, Subscription } from '../../observable';
import { safeFetch, PlayerApiClient as client, areArraysSameUnordered, formatWithTemplate, transformMathJsValue } from "../../services/utilities";
import { BCol, BRow, BButton, BFormInput, BTr, BTd, BTh, BTableSimple, BThead, BTbody } from "bootstrap-vue-next";
import FilterableSelect from '../FilterableSelect.vue';
import { ColumnInfo } from "../../../services/restclient";
import { PluginServices } from '../../managers/pluginManager';



interface ColumnDataInfo {
    valueFormat: string | null;
    valueConverter: string | null;

    selectedColumn: ColumnInfo | null;

}


type PluginState = {
    columnDataInfos: ColumnDataInfo[];
}


interface ListProps {
    showMenu?: boolean,
}
// Define component props with default values
const props = withDefaults(defineProps<ListProps>(), {
    showMenu: false, // Default value for showMenu
});

const pluginState = ref<PluginState>({ columnDataInfos: [] });



const pluginService = inject<PluginServices>('pluginService');
if (!pluginService) {
    throw new Error('Plugin service not found!');
}




let subscription: Subscription = EmptySubscription;


const availableColumns = ref<ColumnInfo[]>([]);
const displayData = ref<TimeseriesDataPoint>({ timestamp: 0, values: {} });

const handleAddRow = () => {
    pluginState.value.columnDataInfos.push({
        valueFormat: '{value:F2}',
        valueConverter: 'value * 1',
        selectedColumn: null
    });
};
const handleRemoveRow = (index: number) => {
    pluginState.value.columnDataInfos.splice(index, 1);
};


const showValue = (key?: string) => {
    if (!key) { return 'no key value'; }

    const hasData = displayData.value.values && Object.keys(displayData.value.values).length > 0;
    if (!hasData) { return 'no data'; }
    const value = displayData.value.values[key];
    return formatValue(value, key);
}
const formatValue = (value: number | number[], key: string): string => {
    const columnInfo = pluginState.value.columnDataInfos.find((x) => x.selectedColumn?.name === key);
    if (columnInfo) {

        // Scalar formatting
        if (typeof value === 'number') {
            if (columnInfo?.valueConverter) {
                value = transformMathJsValue(value, columnInfo.valueConverter);
            }
            if (columnInfo?.valueFormat) {
                return formatWithTemplate(value, columnInfo.valueFormat);
            }
            return String(value);
        }

        // Array formatting
        if (Array.isArray(value)) {
            const formatted = value.map((v) => {
                let result: number | string = v;

                if (columnInfo?.valueConverter) {
                    result = transformMathJsValue(v, columnInfo.valueConverter);
                }

                if (columnInfo?.valueFormat) {
                    return formatWithTemplate(result, columnInfo.valueFormat);
                }

                return String(result);
            });

            return `[${formatted.join(', ')}]`;
        }
    }
    return String(value);
};


onMounted(async () => {

    pluginState.value = pluginService.getPluginState() as PluginState || pluginState.value;
    await loadColumns();

    subscription = pluginService.getDataManager().measurement$.subscribe((data) => {
        displayData.value = data;
        console.log('Data received:', data);
    });

    const initialColumnNames = pluginState.value.columnDataInfos.map((x) => x.selectedColumn?.name).filter((x) => x !== undefined) as string[];


    // load the new columns
    await pluginService.getDataManager().initialize(initialColumnNames);


});

onUnmounted(() => {
    subscription?.unsubscribe();
});



watch(pluginState, async (newValue) => {

    // if new columns are added, load them
    const actualColumnNames = pluginService.getDataManager().getColumnNames().map(x => x.name);
    const newColumnNames = newValue.columnDataInfos.map((x) => x.selectedColumn?.name).filter((x) => x !== undefined) as string[];
    // check if the values are not the same
    const areArraysSame = areArraysSameUnordered(actualColumnNames, newColumnNames);
    if (!areArraysSame) {
        // load the new columns
        await pluginService.getDataManager().initialize(newColumnNames);
    }


    pluginService.savePluginState(newValue);
}, { deep: true });




const loadColumns = async () => {
    const [error, response] = await safeFetch(() => client.getDataApiV1PlayerColumnsGet());
    if (response) {

        const numericColumns = response.columns.filter((c: any) => c.type.includes('int') || c.type.includes('float'));
        const arrayColumns = response.columns.filter((c: any) => c.type.includes('object') || c.type.includes('array'));

        // console.log('Numeric Columns loaded', numericColumns);
        availableColumns.value = [...numericColumns, ...arrayColumns]; //.map(x => ({ text: x.name, value: x }));


    }
    if (error) {
        console.error('Error loading columns:', error);
    }
}

</script>



<style scoped>
.data-list-table {
    width: 100%;
    /* Ensure the table takes full width of its container */
}

.column-header,
.column-cell {
    width: 1%;
    /* Make the column take minimum width */
    white-space: nowrap;
    /* Prevent text from wrapping */
}

.value-header,
.value-cell {
    width: 99%;
}

.value-cell {
    font-family: monospace;
    padding-left: 10px;
}
</style>