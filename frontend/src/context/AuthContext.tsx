import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types/api';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  devLogin: () => void;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>({
    id: 2,
    username: 'analyst',
    email: 'analyst@cyber-soc.local',
    full_name: 'Senior SOC Analyst',
    role: 'analyst'
  });
  const [token, setToken] = useState<string | null>(localStorage.getItem('cyber_token') || 'dev-analyst-token');
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    const savedToken = localStorage.getItem('cyber_token');
    if (savedToken) {
      setToken(savedToken);
      api.getMe()
        .then(u => setUser(u))
        .catch(() => {
          // If token expired, fallback to dev analyst
          setUser({
            id: 2,
            username: 'analyst',
            email: 'analyst@cyber-soc.local',
            full_name: 'Senior SOC Analyst',
            role: 'analyst'
          });
        });
    }
  }, []);

  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      const res = await api.login(username, password);
      localStorage.setItem('cyber_token', res.access_token);
      setToken(res.access_token);
      const me = await api.getMe();
      setUser(me);
    } finally {
      setLoading(false);
    }
  };

  const devLogin = () => {
    localStorage.setItem('cyber_token', 'dev-analyst-token');
    setToken('dev-analyst-token');
    setUser({
      id: 2,
      username: 'analyst',
      email: 'analyst@cyber-soc.local',
      full_name: 'Senior SOC Analyst (Dev Mode)',
      role: 'analyst'
    });
  };

  const logout = () => {
    localStorage.removeItem('cyber_token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, devLogin, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
