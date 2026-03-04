"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { toast } from "sonner";
import Link from "next/link";
import { Activity, ArrowRight, ShieldCheck } from "lucide-react";

const ticketSchema = z.object({
    title: z.string().min(5, "Title must be at least 5 characters"),
    description: z.string().min(10, "Description must be at least 10 characters"),
});

type TicketFormData = z.infer<typeof ticketSchema>;

export default function Home() {
    const [isLoading, setIsLoading] = useState(false);
    const { register, handleSubmit, formState: { errors }, reset } = useForm<TicketFormData>({
        resolver: zodResolver(ticketSchema),
    });

    const onSubmit = async (data: TicketFormData) => {
        setIsLoading(true);
        try {
            await Api.customer.createTicket(data);
            toast.success("Ticket submitted successfully! Our team will be with you shortly.");
            reset();
        } catch (error: any) {
            toast.error(error?.data?.detail?.[0]?.msg || "Failed to submit ticket.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="relative min-h-screen flex flex-col items-center justify-center p-4 overflow-hidden bg-background">
            {/* Animated Background Decorators */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-primary/20 blur-[120px] animate-blob"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-cyan-600/20 blur-[120px] animate-blob animation-delay-2000"></div>
                <div className="absolute top-[40%] left-[60%] w-[30%] h-[30%] rounded-full bg-blue-500/10 blur-[100px] animate-blob animation-delay-4000"></div>
                <div className="absolute inset-0 bg-grid-white/[0.02]"></div>
            </div>

            {/* Header Navigation */}
            <div className="absolute top-0 left-0 right-0 p-6 flex justify-between items-center z-10 max-w-7xl mx-auto w-full">
                <div className="flex items-center gap-2 font-bold text-xl tracking-tight">
                    <div className="bg-primary/20 p-2 rounded-lg border border-primary/50">
                        <Activity className="h-5 w-5 text-primary" />
                    </div>
                    <span>Smart <span className="gradient-text">Triage</span></span>
                </div>
                <Link href="/login">
                    <Button variant="ghost" className="rounded-full px-6 hover:bg-white/5 border border-transparent hover:border-white/10 transition-all">
                        Agent Portal <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                </Link>
            </div>

            {/* Main Content */}
            <div className="w-full max-w-lg z-10 pt-16 animate-in fade-in slide-in-from-bottom-8 duration-1000">
                <div className="text-center mb-10 space-y-4">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-sm font-medium mb-4">
                        <ShieldCheck className="h-4 w-4 text-primary" />
                        <span className="text-muted-foreground">Secure & Encrypted Support</span>
                    </div>
                    <h1 className="text-5xl font-extrabold tracking-tight lg:text-6xl mb-4 gradient-text drop-shadow-sm pb-2">
                        How can we help?
                    </h1>
                    <p className="text-muted-foreground text-lg max-w-[80%] mx-auto">
                        Submit a detailed request below, and our intelligent routing system will connect you with the right expert instantly.
                    </p>
                </div>

                <Card className="glass-card border-none ring-1 ring-white/10 overflow-hidden relative group">
                    <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>

                    <CardHeader className="pb-6 relative z-10 border-b border-white/5 bg-white/[0.02]">
                        <CardTitle className="text-2xl font-semibold">Submit a Ticket</CardTitle>
                        <CardDescription className="text-base text-muted-foreground/80">
                            Please provide as much detail as possible to speed up resolution.
                        </CardDescription>
                    </CardHeader>
                    <form onSubmit={handleSubmit(onSubmit)} className="relative z-10">
                        <CardContent className="space-y-5 pt-6">
                            <div className="space-y-2">
                                <Label htmlFor="title" className="text-foreground/80 font-medium">Issue Title</Label>
                                <Input
                                    id="title"
                                    className="bg-white/5 border-white/10 focus-visible:ring-primary/50 h-12 text-base transition-colors hover:bg-white/10"
                                    placeholder="E.g., Cannot access my account dashboard"
                                    {...register("title")}
                                />
                                {errors.title && (
                                    <p className="text-sm text-destructive font-medium animate-in slide-in-from-top-1">{errors.title.message}</p>
                                )}
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="description" className="text-foreground/80 font-medium">Detailed Description</Label>
                                <Textarea
                                    id="description"
                                    className="bg-white/5 border-white/10 focus-visible:ring-primary/50 text-base transition-colors hover:bg-white/10 resize-none"
                                    placeholder="Please describe what happened, what you expected to happen, and any steps to reproduce the issue..."
                                    rows={6}
                                    {...register("description")}
                                />
                                {errors.description && (
                                    <p className="text-sm text-destructive font-medium animate-in slide-in-from-top-1">{errors.description.message}</p>
                                )}
                            </div>
                        </CardContent>
                        <CardFooter className="pb-8 pt-4">
                            <Button
                                type="submit"
                                size="lg"
                                className="w-full h-12 text-base font-semibold shadow-[0_0_20px_rgba(var(--primary),0.3)] hover:shadow-[0_0_30px_rgba(var(--primary),0.5)] transition-all duration-300"
                                disabled={isLoading}
                            >
                                {isLoading ? (
                                    <span className="flex items-center gap-2">
                                        <div className="h-4 w-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                                        Processing...
                                    </span>
                                ) : "Submit Ticket Securely"}
                            </Button>
                        </CardFooter>
                    </form>
                </Card>

                <p className="text-center text-sm text-muted-foreground mt-8">
                    By submitting a ticket, you agree to our <a href="#" className="underline hover:text-foreground transition-colors">Terms of Service</a> and <a href="#" className="underline hover:text-foreground transition-colors">Privacy Policy</a>.
                </p>
            </div>
        </div>
    );
}
