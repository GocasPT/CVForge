<script lang="ts" setup>
defineProps<{ pdfPath: string }>()
</script>

<template>
  <div class="mt-4 border rounded-lg p-4 bg-gray-50">
    <h4 class="font-semibold mb-2">Preview</h4>

    <iframe
      v-if="pdfPath"
      :src="pdfPath"
      class="w-full h-[600px] border rounded"
    ></iframe>

    <p v-else class="text-gray-500 text-sm">No preview available</p>
  </div>
</template>
