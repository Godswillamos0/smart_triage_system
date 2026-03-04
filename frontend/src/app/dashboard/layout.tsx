"use client";

import { useAuth } from "@/components/providers/auth-provider";
import { Button } from "@/components/ui/button";
import { LogOut, Activity } from "lucide-react";
import Link from "next/link";

export default function DashboardLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    const { logout, userId } = useAuth();

    return (
        <div className="relative min-h-screen bg-background flex flex-col overflow-hidden">
            {/* Ambient Background */}
            <div className="fixed top-0 left-0 w-full h-[300px] bg-gradient-to-b from-primary/10 to-transparent pointer-events-none z-0"></div>

            {/* Top Navbar */}
            <header className="sticky top-0 z-50 w-full border-b border-white/5 bg-background/60 backdrop-blur-xl supports-[backdrop-filter]:bg-background/40">
                <div className="container max-w-7xl flex h-16 items-center justify-between">
                    <div className="flex items-center gap-2 font-bold text-lg tracking-tight">
                        <div className="bg-primary/20 p-2 rounded-lg border border-primary/50">
                            <Activity className="h-4 w-4 text-primary" />
                        </div>
                        <span>Smart <span className="gradient-text">Triage Desk</span></span>
                    </div>

                    <div className="flex items-center gap-4">
                        <span className="text-sm font-medium px-3 py-1 rounded-full bg-white/5 border border-white/10 hidden sm:inline-flex items-center gap-2">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                            </span>
                            Agent: {userId?.substring(0, 8)}...
                        </span>
                        <Button variant="ghost" size="sm" onClick={logout} className="hover:bg-destructive/20 hover:text-destructive transition-colors">
                            <LogOut className="mr-2 h-4 w-4" />
                            Sign Out
                        </Button>
                    </div>
                </div>
            </header>

            {/* Main Content Area */}
            <main className="flex-1 container py-8 w-full max-w-7xl mx-auto relative z-10 animate-in fade-in slide-in-from-bottom-4 duration-500">
                {children}
            </main>
        </div>
    );
}
