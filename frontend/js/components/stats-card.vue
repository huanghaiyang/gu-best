<script setup>

const props = defineProps({
    title: {
        type: String,
        required: true
    },
    value: {
        type: [String, Number],
        default: '-'
    },
    valueClass: {
        type: String,
        default: ''
    }
});
</script>

<template>
    <div class="card stat-card">
        <div class="stat-value" :class="valueClass">{{ value }}</div>
        <div class="stat-label">{{ title }}</div>
    </div>
</template>