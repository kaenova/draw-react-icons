import { useEffect, useState } from 'react';

function getStorageValue(key: string, defaultValue: string) {
  if (typeof window == 'undefined') return defaultValue;
  // getting stored value
  let val = window.localStorage.getItem(key);
  if (!!!val) {
    val = defaultValue;
  }
  return val;
}

export const useLocalStorage = (key: string, defaultValue: string) => {
  const state = useState(() => {
    return getStorageValue(key, defaultValue);
  });

  useEffect(() => {
    // storing input name
    localStorage.setItem(key, state[0]);
  }, [key, state[0]]);

  return state;
};
