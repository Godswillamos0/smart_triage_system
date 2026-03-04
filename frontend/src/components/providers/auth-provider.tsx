"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Api, LoginRequest, LoginResponse } from "@/lib/api";

interface AuthContextType {
    token: string | null;
    userId: string | null;
    login: (credentials: LoginRequest) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [token, setToken] = useState<string | null>(null);
    const [userId, setUserId] = useState<string | null>(null);
    const [isMounted, setIsMounted] = useState(false);
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        // Initialize from local storage on mount
        const storedToken = localStorage.getItem("token");
        const storedUserId = localStorage.getItem("userId");
        if (storedToken && storedUserId) {
            setToken(storedToken);
            setUserId(storedUserId);
        }
        setIsMounted(true);
    }, []);

    const login = async (credentials: LoginRequest) => {
        // Note: the provided openapi spec shows POST /api/v1/auth/login with a JSON body 
        // instead of OAuth2 Form Data, so the API client is using JSON stringify.
        const res = await Api.auth.login(credentials);
        const access_token = res.access_token;

        setToken(access_token);
        setUserId(res.user_id);
        localStorage.setItem("token", access_token);
        localStorage.setItem("userId", res.user_id);

        router.push("/dashboard");
    };

    const logout = () => {
        setToken(null);
        setUserId(null);
        localStorage.removeItem("token");
        localStorage.removeItem("userId");
        router.push("/login");
    };

    const isAuthenticated = !!token;

    // Protect routes - naive client side protection
    useEffect(() => {
        if (!isMounted) return;
        const isProtectedRoute = pathname.startsWith("/dashboard");
        if (isProtectedRoute && !isAuthenticated) {
            router.push("/login");
        }
    }, [isAuthenticated, pathname, router, isMounted]);

    return (
        <AuthContext.Provider value={{ token, userId, login, logout, isAuthenticated }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
