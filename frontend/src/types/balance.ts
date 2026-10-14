export type QualityStatus = 'valid' | 'incomplete' | 'estimated' | "invalid";

export type BalanceSummary = {
    start_time: string;
    end_time: string;
    
    total_production_energy_kwh: number;
    total_consumption_energy_kwh: number;
    total_net_energy_kwh: number;

    quality_status: QualityStatus;
};

export type BalanceInterval = {
    interval_start: string;
    interval_end: string;

    avg_production_power_kw: number;
    avg_consumption_power_kw: number;
    avg_net_power_kw: number;
    
    production_energy_kwh: number;
    consumption_energy_kwh: number;
    net_energy_kwh: number;

    quality_status: QualityStatus;
};