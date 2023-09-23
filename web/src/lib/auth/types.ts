export type AuthContextType = {
  isAuth: boolean | null;
  token: string | null;
  setToken: React.Dispatch<React.SetStateAction<string>>;
};
