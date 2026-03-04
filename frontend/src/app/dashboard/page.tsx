"use client";

import { useEffect, useState, useCallback } from "react";
import { Api, TicketResponse } from "@/lib/api";
import { toast } from "sonner";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, FilterX } from "lucide-react";

const LIMIT = 10;

export default function DashboardPage() {
    const [tickets, setTickets] = useState<TicketResponse[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    // Pagination & Filter State
    const [skip, setSkip] = useState(0);
    const [filterStatus, setFilterStatus] = useState<string>("all");
    const [filterPriority, setFilterPriority] = useState<string>("all");
    const [filterCategory, setFilterCategory] = useState<string>("all");
    const [hasMore, setHasMore] = useState(true);

    const fetchTickets = useCallback(async () => {
        try {
            setIsLoading(true);
            const data = await Api.ticket.getTickets(
                skip,
                LIMIT,
                filterStatus,
                filterPriority,
                filterCategory
            );
            setTickets(data);
            // If we received fewer items than requested, we're at the end
            setHasMore(data.length === LIMIT);
        } catch (error) {
            toast.error("Failed to load tickets");
        } finally {
            setIsLoading(false);
        }
    }, [skip, filterStatus, filterPriority, filterCategory]);

    useEffect(() => {
        fetchTickets();
    }, [fetchTickets]);

    const handleFilterChange = (setter: React.Dispatch<React.SetStateAction<string>>) => (val: string) => {
        setter(val);
        setSkip(0); // Reset pagination on filter change
    };

    const clearFilters = () => {
        setFilterStatus("all");
        setFilterPriority("all");
        setFilterCategory("all");
        setSkip(0);
    };

    const handleStatusChange = async (ticketId: string, newStatus: string) => {
        // Optimistic Update
        setTickets((prev) =>
            prev.map((t) => (t.id === ticketId ? { ...t, status: newStatus } : t))
        );

        try {
            await Api.ticket.updateTicketStatus(ticketId, {
                status: newStatus as any,
            });
            toast.success("Ticket status updated");
        } catch (error) {
            toast.error("Failed to update status");
            // Revert on failure
            fetchTickets();
        }
    };

    const statusColors: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
        open: "destructive",
        in_progress: "default",
        resolved: "secondary",
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-500 pb-10">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 bg-card/40 backdrop-blur-md p-6 rounded-2xl border border-white/10 shadow-lg relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-[80px] -z-10 pointer-events-none translate-x-1/2 -translate-y-1/2"></div>

                <div className="z-10">
                    <h2 className="text-3xl font-bold tracking-tight mb-2">Active Tickets</h2>
                    <p className="text-muted-foreground text-base">
                        Manage and resolve customer submissions efficiently.
                    </p>
                </div>

                {/* Filters */}
                <div className="flex flex-wrap items-center gap-3 z-10 bg-background/50 p-2 rounded-xl border border-white/5">
                    <Select value={filterStatus} onValueChange={handleFilterChange(setFilterStatus)}>
                        <SelectTrigger className="w-[140px] h-[38px] bg-white/5 border-white/10 hover:bg-white/10 transition-colors">
                            <SelectValue placeholder="Status" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Statuses</SelectItem>
                            <SelectItem value="open">Open</SelectItem>
                            <SelectItem value="in_progress">In Progress</SelectItem>
                            <SelectItem value="resolved">Resolved</SelectItem>
                        </SelectContent>
                    </Select>

                    <Select value={filterPriority} onValueChange={handleFilterChange(setFilterPriority)}>
                        <SelectTrigger className="w-[140px] h-[38px] bg-white/5 border-white/10 hover:bg-white/10 transition-colors">
                            <SelectValue placeholder="Priority" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Priorities</SelectItem>
                            <SelectItem value="low">Low</SelectItem>
                            <SelectItem value="medium">Medium</SelectItem>
                            <SelectItem value="high">High</SelectItem>
                        </SelectContent>
                    </Select>

                    <Select value={filterCategory} onValueChange={handleFilterChange(setFilterCategory)}>
                        <SelectTrigger className="w-[160px] h-[38px] bg-white/5 border-white/10 hover:bg-white/10 transition-colors">
                            <SelectValue placeholder="Category" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Categories</SelectItem>
                            <SelectItem value="technical_bug">Technical Bug</SelectItem>
                            <SelectItem value="feature_request">Feature Request</SelectItem>
                            <SelectItem value="billing">Billing</SelectItem>
                            <SelectItem value="other">Other</SelectItem>
                        </SelectContent>
                    </Select>

                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={clearFilters}
                        className="h-[38px] px-3 text-muted-foreground hover:text-foreground hover:bg-white/10 rounded-lg transition-colors"
                    >
                        <FilterX className="h-4 w-4 mr-2" /> Clear
                    </Button>
                </div>
            </div>

            <Card className="glass-card shadow-2xl border border-white/10 overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-b from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-1000 pointer-events-none"></div>

                <CardHeader className="border-b border-white/5 bg-white/[0.01]">
                    <div className="flex items-center justify-between">
                        <div>
                            <CardTitle className="text-xl">Support Requests</CardTitle>
                            <CardDescription>
                                Showing page {Math.floor(skip / LIMIT) + 1}
                            </CardDescription>
                        </div>
                    </div>
                </CardHeader>
                <CardContent className="p-0">
                    {isLoading && tickets.length === 0 ? (
                        <div className="flex items-center justify-center p-20 text-muted-foreground">
                            <div className="flex flex-col items-center gap-4">
                                <div className="h-8 w-8 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
                                <span className="animate-pulse font-medium tracking-wide">Gathering data...</span>
                            </div>
                        </div>
                    ) : tickets.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-24 text-muted-foreground bg-white/[0.01]">
                            <div className="bg-white/5 p-4 rounded-full mb-4 ring-1 ring-white/10">
                                <FilterX className="h-8 w-8 text-muted-foreground/50" />
                            </div>
                            <p className="mb-4 text-base font-medium">No tickets found matching your criteria.</p>
                            <Button variant="outline" onClick={clearFilters} className="bg-transparent border-white/20 hover:bg-white/10 transition-colors">
                                Clear all filters
                            </Button>
                        </div>
                    ) : (
                        <div className="flex flex-col h-full">
                            <div className="overflow-x-auto">
                                <Table>
                                    <TableHeader className="bg-background/40">
                                        <TableRow className="border-b border-white/5 hover:bg-transparent">
                                            <TableHead className="w-[100px] text-xs font-semibold uppercase tracking-wider text-muted-foreground h-12">Ticket ID</TableHead>
                                            <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Title</TableHead>
                                            <TableHead className="hidden md:table-cell text-xs font-semibold uppercase tracking-wider text-muted-foreground">Description</TableHead>
                                            <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Priority</TableHead>
                                            <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Category</TableHead>
                                            <TableHead className="w-[180px] text-xs font-semibold uppercase tracking-wider text-muted-foreground text-right pr-6">Status</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {tickets.map((ticket) => (
                                            <TableRow
                                                key={ticket.id}
                                                className="group border-b border-white/5 bg-transparent hover:bg-white/[0.04] transition-colors duration-200"
                                            >
                                                <TableCell className="font-mono text-xs text-muted-foreground/70 py-4">
                                                    {ticket.id.substring(0, 8)}
                                                </TableCell>
                                                <TableCell className="font-medium text-foreground py-4">{ticket.title}</TableCell>
                                                <TableCell className="hidden md:table-cell max-w-[280px] truncate text-muted-foreground/80 py-4" title={ticket.description}>
                                                    {ticket.description}
                                                </TableCell>
                                                <TableCell className="py-4">
                                                    <Badge
                                                        variant={ticket.priority === 'critical' || ticket.priority === 'high' ? 'destructive' : 'outline'}
                                                        className={`capitalize font-medium shadow-sm ${ticket.priority === 'high' || ticket.priority === 'critical' ? 'shadow-destructive/20' : ''}`}
                                                    >
                                                        {ticket.priority || "Normal"}
                                                    </Badge>
                                                </TableCell>
                                                <TableCell className="py-4">
                                                    <span className="text-[13px] font-medium border border-white/10 py-1 px-2.5 rounded-md bg-white/5 capitalize text-foreground/80 whitespace-nowrap shadow-sm">
                                                        {(ticket.category || "other").replace("_", " ")}
                                                    </span>
                                                </TableCell>
                                                <TableCell className="py-4 pr-6">
                                                    <div className="flex justify-end">
                                                        <Select
                                                            defaultValue={ticket.status}
                                                            onValueChange={(val) => handleStatusChange(ticket.id, val)}
                                                        >
                                                            <SelectTrigger className="h-9 w-[150px] bg-background/50 border-white/10 hover:bg-white/10 transition-colors shadow-sm">
                                                                <SelectValue>
                                                                    <div className="flex items-center gap-2">
                                                                        <div className={`w-2 h-2 rounded-full ${ticket.status === 'open' ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]' :
                                                                                ticket.status === 'in_progress' ? 'bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]' :
                                                                                    'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]'
                                                                            }`}></div>
                                                                        <span className="capitalize">{ticket.status.replace("_", " ")}</span>
                                                                    </div>
                                                                </SelectValue>
                                                            </SelectTrigger>
                                                            <SelectContent>
                                                                <SelectItem value="open">
                                                                    <div className="flex items-center gap-2">
                                                                        <div className="w-2 h-2 rounded-full bg-red-500"></div>Open
                                                                    </div>
                                                                </SelectItem>
                                                                <SelectItem value="in_progress">
                                                                    <div className="flex items-center gap-2">
                                                                        <div className="w-2 h-2 rounded-full bg-blue-500"></div>In Progress
                                                                    </div>
                                                                </SelectItem>
                                                                <SelectItem value="resolved">
                                                                    <div className="flex items-center gap-2">
                                                                        <div className="w-2 h-2 rounded-full bg-emerald-500"></div>Resolved
                                                                    </div>
                                                                </SelectItem>
                                                            </SelectContent>
                                                        </Select>
                                                    </div>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </div>

                            {/* Pagination Controls */}
                            <div className="flex items-center justify-between p-4 border-t border-white/5 bg-white/[0.01]">
                                <p className="text-sm text-muted-foreground font-medium">
                                    {isLoading ? (
                                        <span className="flex items-center gap-2">
                                            <div className="h-3 w-3 border-2 border-primary/30 border-t-primary rounded-full animate-spin"></div>
                                            Syncing...
                                        </span>
                                    ) : (
                                        `Showing ${tickets.length === 0 ? 0 : skip + 1} to ${skip + tickets.length}`
                                    )}
                                </p>
                                <div className="flex items-center space-x-2">
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => setSkip((s) => Math.max(0, s - LIMIT))}
                                        disabled={skip === 0 || isLoading}
                                        className="bg-transparent border-white/10 hover:bg-white/10 transition-colors h-9"
                                    >
                                        <ChevronLeft className="h-4 w-4 mr-1" />
                                        Previous
                                    </Button>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => setSkip((s) => s + LIMIT)}
                                        disabled={!hasMore || isLoading}
                                        className="bg-transparent border-white/10 hover:bg-white/10 transition-colors h-9"
                                    >
                                        Next
                                        <ChevronRight className="h-4 w-4 ml-1" />
                                    </Button>
                                </div>
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
