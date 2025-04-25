<template>
    <BFormInput :value="localValue" @input="localValue = $event" @blur="emitUpdate" v-bind="$attrs" />
</template>

<script setup lang="ts">
import { BFormInput } from "bootstrap-vue-next";
import { ref, watch } from 'vue'

const props = defineProps<{
    modelValue: string | null | undefined
}>()


const emit = defineEmits<{
    (e: 'update:modelValue', value: string): void
}>()

const localValue = ref(props.modelValue)

// Keep localValue in sync when modelValue changes externally
watch(() => props.modelValue, (newVal) => {
    if (newVal !== localValue.value) {
        localValue.value = newVal
    }
})

const emitUpdate = () => {
    emit('update:modelValue', localValue.value || '')
}
</script>
