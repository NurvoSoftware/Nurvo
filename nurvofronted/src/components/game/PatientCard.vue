<script setup lang="ts">
import type { PatientProfile } from '@/types/game'

defineProps<{
  patient: PatientProfile
  painSeverity?: number
}>()
</script>

<template>
  <div class="patient-card">
    <!-- Top row: avatar + name on left, pain badge on right -->
    <div class="patient-top-row">
      <div class="patient-identity">
        <div class="patient-avatar">&#x1F9D3;</div>
        <div class="patient-name-block">
          <span class="patient-name">{{ patient.name }}</span>
          <span class="patient-meta">{{ patient.age }} 歲 ・ {{ patient.gender }}</span>
        </div>
      </div>
      <div v-if="painSeverity != null" class="pain-badge">
        疼痛等級: {{ painSeverity }}/10
      </div>
    </div>

    <!-- Info boxes row -->
    <div class="info-boxes">
      <div class="info-box">
        <span class="info-label">診斷</span>
        <span class="info-value">{{ patient.diagnosis }}</span>
      </div>
      <div class="info-box">
        <span class="info-label">目前用藥</span>
        <span class="info-value">{{ patient.medications.join('、') || '無' }}</span>
      </div>
    </div>

    <!-- Tags row -->
    <div class="tags-section">
      <div v-if="patient.medical_history.length" class="tags-group">
        <span class="tags-label">過去病史</span>
        <div class="tags-row">
          <span
            v-for="item in patient.medical_history"
            :key="item"
            class="tag tag-blue"
          >{{ item }}</span>
        </div>
      </div>

      <div class="tags-group">
        <span class="tags-label">過敏史</span>
        <div class="tags-row">
          <span
            v-for="allergy in patient.allergies"
            :key="allergy"
            class="tag tag-red"
          >{{ allergy }}</span>
          <span v-if="patient.allergies.length === 0" class="tag tag-blue">
            無已知過敏
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.patient-card {
  background: var(--nurvo-white);
  border: 1px solid var(--nurvo-border);
  border-radius: var(--nurvo-radius-lg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: var(--nurvo-shadow-card);
}

/* ---- Top row ---- */
.patient-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.patient-identity {
  display: flex;
  align-items: center;
  gap: 12px;
}

.patient-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--nurvo-patient-light), var(--nurvo-patient));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.patient-name-block {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.patient-name {
  font-size: var(--nurvo-font-size-xl);
  font-weight: 700;
  color: var(--nurvo-text-primary);
  line-height: 1.3;
}

.patient-meta {
  font-size: var(--nurvo-font-size-base);
  color: var(--nurvo-text-secondary);
  line-height: 1.3;
}

.pain-badge {
  flex-shrink: 0;
  background: var(--nurvo-danger-light);
  color: var(--nurvo-danger-dark);
  font-size: var(--nurvo-font-size-base);
  font-weight: 600;
  padding: 4px 12px;
  border-radius: var(--nurvo-radius-pill);
  white-space: nowrap;
}

/* ---- Info boxes ---- */
.info-boxes {
  display: flex;
  gap: 12px;
}

.info-box {
  flex: 1;
  background: var(--nurvo-surface);
  border-radius: 10px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: var(--nurvo-font-size-sm);
  font-weight: 500;
  color: var(--nurvo-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.info-value {
  font-size: var(--nurvo-font-size-md);
  font-weight: 600;
  color: var(--nurvo-text-primary);
  line-height: 1.4;
}

/* ---- Tags ---- */
.tags-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tags-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tags-label {
  font-size: var(--nurvo-font-size-sm);
  font-weight: 500;
  color: var(--nurvo-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  display: inline-block;
  font-size: var(--nurvo-font-size-base);
  font-weight: 500;
  padding: 3px 10px;
  border-radius: var(--nurvo-radius-pill);
  line-height: 1.5;
}

.tag-blue {
  background: var(--nurvo-primary-light);
  color: var(--nurvo-primary);
  border: 1px solid var(--nurvo-primary-border);
}

.tag-red {
  background: var(--nurvo-danger-light);
  color: var(--nurvo-danger-dark);
  border: 1px solid var(--nurvo-danger-border);
}
</style>
