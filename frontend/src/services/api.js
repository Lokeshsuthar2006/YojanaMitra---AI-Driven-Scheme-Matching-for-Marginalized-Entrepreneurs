const BASE = 'http://127.0.0.1:8000/api';
async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, {headers: {'Content-Type': 'application/json'}, ...options});
  if (!response.ok) throw new Error((await response.json().catch(() => ({}))).detail || 'Unable to connect to Yojana Mitra services. Please try again.');
  return response.json();
}
export const api = {
  demos: () => request('/demo/profiles'),
  eligibility: (profile) => request('/eligibility/check', {method:'POST', body:JSON.stringify(profile)}),
  finance: (values) => request('/finance/calculate', {method:'POST', body:JSON.stringify(values)}),
  nearby: (values) => request('/partners/nearby', {method:'POST', body:JSON.stringify(values)}),
  explain: (result) => request('/ai/explain', {method:'POST', body:JSON.stringify({result})}),
};
