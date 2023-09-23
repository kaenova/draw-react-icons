import React, { useEffect } from 'react';
import { AuthContext } from './context';
import api from '../api';
import { useLocalStorage } from '@/hooks/useLocalStorage';

function AuthProvider({ children }: { children: React.ReactNode }) {
  const [Token, setToken] = useLocalStorage('rd-a', '');
  const [IsAuth, setIsAuth] = React.useState<boolean | null>(null);

  const checkAuth = async () => {
    if (!window) return;
    setIsAuth(null);
    try {
      const res = await api.get('/auth', { params: { token: Token } });
      setIsAuth(res.data);
    } catch (e) {
      console.error(e);
      setIsAuth(false);
    }
  };

  useEffect(() => {
    const id = setTimeout(() => {
      checkAuth();
    }, 2000);
    return () => {
      clearTimeout(id);
    };
  }, [Token]);

  return (
    <AuthContext.Provider
      value={{ isAuth: IsAuth, setToken: setToken, token: Token }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export default AuthProvider;
