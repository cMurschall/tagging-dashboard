<template>
  <BDropdown :text="selectedLabel" class="w-100" variant="outline-dark" block>
    <div class="px-3 pt-2 pb-1">
      <input v-model="filter" type="text" class="form-control" placeholder="Type to filter..." @click.stop
        @keydown.stop />
    </div>

    <BDropdownDivider />

    <BDropdownItem v-for="(option, index) in filteredOptions" :key="index" @click="selectOption(option)">
      {{ getLabel(option) }}
    </BDropdownItem>
  </BDropdown>
</template>

<script setup lang="ts" generic="T">
import { ref, computed } from 'vue'
import { BDropdown, BDropdownItem, BDropdownDivider } from 'bootstrap-vue-next'
import { isNullOrUndefined } from '../core/utilities/utilities';

const props = defineProps<{
  modelValue: T | null
  options: T[]
  getLabel: (item: T) => string
  placeholder?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: unknown): void
}>()

const filter = ref('')

const selectedLabel = computed(() => {
  const value = props.modelValue

  if (isNullOrUndefined(value)) {
    return props.placeholder || 'Select...'
  }

  const selected = props.options.find(opt => props.getLabel(opt) == props.getLabel(value))
  return selected ? props.getLabel(selected) : props.placeholder || 'Select...'
})

const filteredOptions = computed(() =>
  props.options.filter(opt =>
    props.getLabel(opt).toLowerCase().includes(filter.value.toLowerCase())
  )
)

function selectOption(option: T) {
  emit('update:modelValue', option)
  filter.value = ''
}
</script>
