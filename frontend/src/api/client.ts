import axios from "axios";

const API_BASE = "https://riskflow-api-1odp.onrender.com";

export const getCostAnalysis = () =>
  axios.get(`${API_BASE}/api/cost-analysis`).then((res) => res.data);

export const getThresholdSimulation = (threshold: number) =>
  axios.get(`${API_BASE}/api/threshold-simulator?threshold=${threshold}`).then((res) => res.data);

export const getPipelineHealth = () =>
  axios.get(`${API_BASE}/api/pipeline/health`).then((res) => res.data);
