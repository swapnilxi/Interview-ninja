'use client';

import { createContext, useContext, useEffect, useState } from 'react';

const AuthContext = createContext<any>({});

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

const dummyUser = {
  id: 'local-user-id',
  email: 'user@interviewninja.local',
  user_metadata: {
    full_name: 'Interview Ninja User',
  },
};

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<any>(dummyUser);
  const [session, setSession] = useState<any>({ user: dummyUser });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Synchronously mark auth load complete
    setLoading(false);
  }, []);

  // Email/Password Sign Up
  const signUp = async (email: string, password: string, metadata = {}) => {
    return { user: dummyUser };
  };

  // Email/Password Sign In
  const signIn = async (email: string, password: string) => {
    return { user: dummyUser };
  };

  // Sign Out
  const signOut = async () => {
    setUser(null);
    setSession(null);
  };

  // Get Current User
  const getCurrentUser = async () => {
    return dummyUser;
  };

  // Check if Email is Verified
  const isEmailVerified = () => {
    return true;
  };

  // Get User Profile from Database
  const getUserProfile = async () => {
    return {
      id: 'local-user-id',
      full_name: 'Interview Ninja User',
    };
  };

  const value = {
    user,
    session,
    loading,
    signUp,
    signIn,
    signOut,
    getCurrentUser,
    isEmailVerified,
    getUserProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
