export type QualityStatus = 'valid' | 'incomplete' | 'estimated' | "invalid";

export type BalanceSummary = {
    start_time: string;
    end_time: string;
    
    total_production_energy_kwh: number;
    total_consumption_energy_kwh: number;
    total_net_energy_kwh: number;

    quality_status: QualityStatus;
};