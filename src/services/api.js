import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5000';

export const getLogsCount = async () => {
  const response = await axios.get(`${API_BASE_URL}/logs/count`);
  return response.data;
};

export const getLogs = async () => {
  const response = await axios.get(`${API_BASE_URL}/logs`);
  return response.data;
};

export const verifyChain = async () => {
  const response = await axios.get(`${API_BASE_URL}/verify`);
  return response.data;
};

export const addData = async (data_content) => {
  const response = await axios.post(`${API_BASE_URL}/data`, { data_content });
  return response.data;
};

export const getAlerts = async () => {
  const response = await axios.get(`${API_BASE_URL}/alerts`);
  return response.data;
};

export const getSummary = async () => {
  const response = await axios.get(`${API_BASE_URL}/summary`);
  return response.data;
};

export const getDataRecords = async () => {
  const response = await axios.get(`${API_BASE_URL}/data`);
  return response.data;
};
