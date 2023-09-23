import { createContext, useContext } from 'react';
import { AuthContextType } from './types';

export const AuthContext = createContext<null | AuthContextType>(null);

export const useAuth = () => useContext(AuthContext);
