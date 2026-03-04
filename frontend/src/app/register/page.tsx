"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { toast } from "sonner";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, UserPlus } from "lucide-react";

const registerSchema = z.object({
    name: z.string().min(2, "Name is required"),
    email: z.string().email("Invalid email address"),
    password: z.string().min(6, "Password must be at least 6 characters"),
});

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();

    const { register, handleSubmit, formState: { errors } } = useForm<RegisterFormData>({
        resolver: zodResolver(registerSchema),
    });

    const onSubmit = async (data: RegisterFormData) => {
        setIsLoading(true);
        try {
            await Api.auth.register(data);
            toast.success("Registration successful. Please login.");
            router.push("/login");
        } catch (error: any) {
            toast.error(error?.data?.detail || "Registration failed");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="relative min-h-screen flex flex-col items-center justify-center p-4 overflow-hidden bg-background">
            {/* Animated Background Decorators */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
                <div className="absolute bottom-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary/20 blur-[120px] animate-blob"></div>
                <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-cyan-600/10 blur-[100px] animate-blob animation-delay-4000"></div>
                <div className="absolute inset-0 bg-grid-white/[0.02]"></div>
            </div>

            <div className="w-full max-w-md z-10 animate-in fade-in slide-in-from-bottom-8 duration-700">

                <Link href="/">
                    <Button variant="ghost" className="mb-6 -ml-4 text-muted-foreground hover:text-foreground transition-colors group">
                        <ArrowLeft className="mr-2 h-4 w-4 group-hover:-translate-x-1 transition-transform" />
                        Back to Home
                    </Button>
                </Link>

                <Card className="glass-card border-none ring-1 ring-white/10 overflow-hidden relative group">
                    <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

                    <CardHeader className="space-y-3 pb-6 text-center relative z-10 border-b border-white/5 bg-white/[0.02] pt-8">
                        <div className="mx-auto bg-primary/20 p-3 rounded-full border border-primary/50 w-fit mb-2">
                            <UserPlus className="h-8 w-8 text-primary" />
                        </div>
                        <CardTitle className="text-3xl font-bold tracking-tight">Create an account</CardTitle>
                        <CardDescription className="text-base text-muted-foreground/80">
                            Enter your information to register as a support agent.
                        </CardDescription>
                    </CardHeader>
                    <form onSubmit={handleSubmit(onSubmit)} className="relative z-10">
                        <CardContent className="space-y-5 pt-8">
                            <div className="space-y-2 text-left">
                                <Label htmlFor="name" className="text-foreground/80 font-medium">Full Name</Label>
                                <Input
                                    id="name"
                                    className="bg-white/5 border-white/10 focus-visible:ring-primary/50 h-11 transition-colors hover:bg-white/10"
                                    placeholder="Jane Doe"
                                    {...register("name")}
                                />
                                {errors.name && (
                                    <p className="text-sm text-destructive font-medium animate-in slide-in-from-top-1">{errors.name.message}</p>
                                )}
                            </div>
                            <div className="space-y-2 text-left">
                                <Label htmlFor="email" className="text-foreground/80 font-medium">Email address</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    className="bg-white/5 border-white/10 focus-visible:ring-primary/50 h-11 transition-colors hover:bg-white/10"
                                    placeholder="m@example.com"
                                    {...register("email")}
                                />
                                {errors.email && (
                                    <p className="text-sm text-destructive font-medium animate-in slide-in-from-top-1">{errors.email.message}</p>
                                )}
                            </div>
                            <div className="space-y-2 text-left">
                                <Label htmlFor="password" className="text-foreground/80 font-medium">Password</Label>
                                <Input
                                    id="password"
                                    type="password"
                                    className="bg-white/5 border-white/10 focus-visible:ring-primary/50 h-11 transition-colors hover:bg-white/10"
                                    placeholder="••••••••"
                                    {...register("password")}
                                />
                                {errors.password && (
                                    <p className="text-sm text-destructive font-medium animate-in slide-in-from-top-1">{errors.password.message}</p>
                                )}
                            </div>
                        </CardContent>
                        <CardFooter className="flex flex-col space-y-5 pb-8 pt-4">
                            <Button
                                type="submit"
                                className="w-full h-11 text-base font-semibold shadow-[0_0_15px_rgba(var(--primary),0.2)] hover:shadow-[0_0_25px_rgba(var(--primary),0.4)] transition-all duration-300"
                                disabled={isLoading}
                            >
                                {isLoading ? (
                                    <span className="flex items-center gap-2">
                                        <div className="h-4 w-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                                        Creating account...
                                    </span>
                                ) : "Register Securely"}
                            </Button>
                            <div className="text-sm text-center text-muted-foreground w-full">
                                Already have an account?{" "}
                                <Link href="/login" className="text-primary hover:text-primary/80 transition-colors font-medium">
                                    Log in
                                </Link>
                            </div>
                        </CardFooter>
                    </form>
                </Card>
            </div>
        </div>
    );
}
