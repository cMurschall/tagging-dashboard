<template>

    <div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div @click="showColumns = !showColumns" style="cursor: pointer;">
                <svg v-if="!showColumns" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                    class="feather feather-menu">
                    <line x1="3" y1="12" x2="21" y2="12"></line>
                    <line x1="3" y1="6" x2="21" y2="6"></line>
                    <line x1="3" y1="18" x2="21" y2="18"></line>
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                    class="feather feather-x">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </div>
        </div>
        <BCollapse v-model="showColumns">
            <!-- <BRow>
                <BCol cols="12">
                    <div rule=group>
                        <label for="column-filter-query">"Search Columns:"</label>
                        <BFormInput onfocus="this.value=''" id="column-filter-query" v-model="searchQuery" type="text"
                            autocomplete="off" placeholder="Search columns..." />
                    </div>
                </BCol>
            </BRow> -->
            <BRow>
                <BCol cols="12">
                    <BFormGroup label="Select Columns:">
                        <BFormSelect v-model="selectedColumns" :options="availableColumns" multiple select-size="3" />
                    </BFormGroup>
                </BCol>
            </BRow>
        </BCollapse>
        <div class="data-list-container">

            <ul class="data-list">
                <!-- <li class="data-list-item">
      
                        <div class="data-list-timestamp">
                            {{ displayData.timestamp }}
                        </div>
              
                </li> -->
                <li v-for="(value, key, index) in displayData.values" :key="index" class="data-list-item">

                    <div>
                        <span class="data-list-key">{{ key }}: </span><span class="data-list-value-content">{{ value }}</span>
                    </div>
             

                </li>
            </ul>
        </div>
    </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, inject, watch } from 'vue';
import { IDataManager, TimeseriesDataPoint } from '../../managers/iDataManager';
import { Subscription } from '../../observable';
import * as math from 'mathjs';
import { safeFetch, PlayerApiClient as client } from "../../services/Utilities";
import { BCol, BCollapse, BFormGroup, BFormSelect, BRow, BFormInput } from "bootstrap-vue-next";
import { ColumnInfo } from "../../../services/restclient";



interface BFormSelectColumnInfo {
    text: string;
    value: ColumnInfo;
}


const dataManager = inject<IDataManager>('dataManager');
if (!dataManager) {
    throw new Error('dataManager not provided');
}

const showColumns = ref(false);
const searchQuery = ref('');


const subscription = ref<Subscription | null>(null);
const valueExpressions = ref<{ [key: string]: string }>({});
const selectedColumns = ref<ColumnInfo[]>([]);
const availableColumns = ref<BFormSelectColumnInfo[]>([]);

const displayData = ref<TimeseriesDataPoint>({ timestamp: 0, values: {} });




onMounted(async () => {

    await loadColumns();

    subscription.value = dataManager.measurement$.subscribe((data) => {
        displayData.value = data;
        console.log('Data received:', data);
    });

});

onUnmounted(() => {
    subscription.value?.unsubscribe();
});

watch(selectedColumns, async (newData) => {
    await dataManager.initialize(newData.map(x => x.name));
});




const loadColumns = async () => {
    const [error, response] = await safeFetch(() => client.getDataApiV1PlayerColumnsGet());
    if (response) {

        const numericColumns = response.columns.filter((c: any) => c.type.includes('int') || c.type.includes('float'));

        // console.log('Numeric Columns loaded', numericColumns);
        availableColumns.value = numericColumns.map(x => ({ text: x.name, value: x }));

        // select the first 10 columns
        selectedColumns.value = numericColumns.slice(0, 10);

    }
    if (error) {
        console.error('Error loading columns:', error);
    }
}

</script>



<style scoped>
.data-list-container {
  padding: 4px; /* Reduced padding */
  background-color: #f5f5f5;
  border-radius: 2px;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.1);
}

.data-list-title {
  margin-bottom: 0.5rem; /* Reduced margin */
  font-size: 1.2rem; /* Slightly smaller title */
}

.data-list-loading {
  text-align: center;
  color: #888;
}

.data-list-error {
  color: red;
  text-align: center;
}

.data-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.data-list-item {
  margin-bottom: 3px; /* Reduced margin */
  padding: 3px; /* Reduced padding */
  background-color: white;
  border-radius: 2px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  border: 1px solid #ddd;
}

.data-list-value {
  margin-bottom: 2px; /* Reduced margin */
  font-size: 0.9rem; /* Slightly smaller font */
  display: flex;
  flex-direction: column; /* Stack key and value vertically */
}

.data-list-key {
  font-weight: bold;
  color: #333;
  margin-right: 0; /* Remove right margin */
  margin-bottom: 2px; /* Add margin to key */
}

.data-list-value-content {
  color: #555;
}

.data-list-expression-input {
  margin-left: 10px;
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.9rem;
  width: 100px;
}

.data-list-timestamp {
  margin-top: 0.25rem; /* Reduced margin */
  font-size: 0.7rem; /* Smaller font */
  color: #888;
}

.data-list-no-data {
  text-align: center;
  color: #888;
  font-style: italic;
}
</style>