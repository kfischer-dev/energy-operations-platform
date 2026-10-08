import type { BalanceSummary } from "../types/balance";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function getHealth() {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
        throw new Error('Failed to fetch health status');
    }
    return response.json();
}
export async function getDbHealth() {
    const response = await fetch(`${API_BASE_URL}/health/db`);
    if (!response.ok) {
        throw new Error('Failed to fetch database health status');
    }
    return response.json();
}

export async function getBalanceSummary(
    startTime: string, 
    endTime: string, 
    intervalMinutes?: number
): Promise<BalanceSummary> {
    const params = new URLSearchParams({
        start_time: startTime,
        end_time: endTime,
    });

    if (intervalMinutes !== undefined) {
        params.set('interval_minutes', intervalMinutes.toString());
    }

    const response = await fetch(`${API_BASE_URL}/balance?${params.toString()}`);
    if (!response.ok) {
        throw new Error('Failed to fetch balance summary');
    }
    return response.json();
}