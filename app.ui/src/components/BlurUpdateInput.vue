<template>
  <BFormInput v-model="localValue" @blur="emitUpdate" @keyup.enter="emitUpdate" @keyup.esc="resetLocalValue"
    v-bind="$attrs" />
</template>

<script setup lang="ts">
import { BFormInput } from "bootstrap-vue-next"
import { ref, watchEffect } from 'vue'

const props = defineProps<{
  modelValue: string | null | undefined
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const resetLocalValue = () => {
  localValue.value = props.modelValue ?? ''
}

const localValue = ref('')

// Keep localValue in sync with modelValue
watchEffect(() => {
  localValue.value = props.modelValue ?? ''
})

// Emit only on blur
const emitUpdate = () => {
  emit('update:modelValue', localValue.value)
}
</script>
