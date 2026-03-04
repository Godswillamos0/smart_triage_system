export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

// --- Types based on OpenAPI spec ---

export interface CreateTicketRequest {
    title: string;
    description: string;
}

export interface TicketResponse {
    id: string;
    title: string;
    description: string;
    status: "open" | "in_progress" | "resolved" | string;
    priority: string;
    category: string;
}

export interface TicketStatusRequest {
    status: "open" | "in_progress" | "resolved";
}

export interface LoginRequest {
    email: string;
    password: string;
}

export interface LoginResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    user_id: string;
}

export interface RegisterUserRequest {
    email: string;
    password: string;
    name: string;
}

export interface SendOTP {
    email: string;
}

export interface VerifyOTP {
    email: string;
    otp: string;
}

// --- API Client ---

export class ApiError extends Error {
    constructor(public status: number, public data: any) {
        super(`API Error ${status}`);
        this.name = "ApiError";
    }
}

async function fetchApi<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    // Try to get token if running on client (not Server Component)
    let token = "";
    if (typeof window !== "undefined") {
        token = localStorage.getItem("token") || "";
    }

    const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...((options.headers as Record<string, string>) || {}),
    };

    if (token && !headers.Authorization) {
        headers.Authorization = `Bearer ${token}`;
    }

    const finalOptions: RequestInit = {
        ...options,
        headers,
        credentials: "include", // Ensure cookies are sent
    };

    const response = await fetch(url, finalOptions);

    if (!response.ok) {
        let errorData;
        try {
            errorData = await response.json();
        } catch {
            errorData = { detail: response.statusText };
        }
        throw new ApiError(response.status, errorData);
    }

    if (response.status === 204) {
        return {} as T;
    }

    return response.json();
}

// --- Endpoints ---

export const Api = {
    customer: {
        createTicket: (data: CreateTicketRequest) =>
            fetchApi<TicketResponse>("/api/v1/customer/ticket", {
                method: "POST",
                body: JSON.stringify(data),
            }),
    },
    auth: {
        login: (data: LoginRequest) =>
            fetchApi<LoginResponse>("/api/v1/auth/login", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        register: (data: RegisterUserRequest) =>
            fetchApi<any>("/api/v1/auth/register", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        sendOtp: (data: SendOTP) =>
            fetchApi<any>("/api/v1/auth/send-verification-otp", {
                method: "POST",
                body: JSON.stringify(data),
            }),
        verifyOtp: (data: VerifyOTP) =>
            fetchApi<any>("/api/v1/auth/verify-otp", {
                method: "POST",
                body: JSON.stringify(data),
            }),
    },
    ticket: {
        getTickets: (skip = 0, limit = 10, status?: string, priority?: string, category?: string) => {
            const qs = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() });
            if (status && status !== "all") qs.append("status", status);
            if (priority && priority !== "all") qs.append("priority", priority);
            if (category && category !== "all") qs.append("category", category);
            return fetchApi<TicketResponse[]>(`/api/v1/ticket/ticket?${qs.toString()}`, {
                method: "GET",
            });
        },
        updateTicketStatus: (ticketId: string, data: TicketStatusRequest) =>
            fetchApi<TicketResponse>(`/api/v1/ticket/ticket/${ticketId}`, {
                method: "PATCH",
                body: JSON.stringify(data),
            }),
    },
};
