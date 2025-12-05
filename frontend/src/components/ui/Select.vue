<script setup>
import { cn } from '@/lib/utils'

defineProps({
  modelValue: [String, Number],
  placeholder: String,
  disabled: Boolean,
  options: Array // [{ value, label }]
})

const emit = defineEmits(['update:modelValue'])

const selectClasses = cn(
  'flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm',
  'ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2',
  'focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
)
</script>

<template>
  <select
    :class="selectClasses"
    :value="modelValue"
    :disabled="disabled"
    @change="emit('update:modelValue', $event.target.value)"
  >
    <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
    <option v-for="opt in options" :key="opt.value" :value="opt.value">
      {{ opt.label }}
    </option>
  </select>
</template>
