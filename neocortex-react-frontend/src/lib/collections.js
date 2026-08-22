export const toArray = (payload, key) => {
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload[key])) return payload[key];
  if (payload && typeof payload === 'object') return Object.values(payload);
  return [];
};
