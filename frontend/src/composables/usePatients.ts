import { ref } from 'vue';

interface Patient {
  id: string;
  // add other patient properties here
}

import patientsData from '@/assets/patients.json' assert { type: 'json' };

export function usePatients() {
  const patients = ref<Patient[]>(patientsData);
  const selectedPatient = ref<Patient | null>(null);

  function selectPatient(patientId: string) {
    const found = patients.value.find(patient => patient.id === patientId);
    selectedPatient.value = found || null;
  }

  return {
    patients,
    selectedPatient,
    selectPatient
  };
}