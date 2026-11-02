export const dashboardCards = [
    { id: 'production', label: 'Production Energy' },
    { id: 'consumption', label: 'Consumption Energy' },
    { id: 'net', label: 'Total Net Energy' },
    { id: 'peak', label: 'Peak Power Deficit' },
    { id: 'balance', label: 'Energy Balance' },
    { id: 'productionMix', label: 'Production Energy Mix' },
    { id: 'consumerMix', label: 'Consumer Energy Mix' },
    { id: 'assets', label: 'Asset Overview' },
] as const;

export type DashboardCardId = typeof dashboardCards[number]['id'];
export type DashboardCardVisibility = Record<DashboardCardId, boolean>;

export const allDashboardCardsVisible: DashboardCardVisibility = {
    production: true,
    consumption: true,
    net: true,
    peak: true,
    balance: true,
    productionMix: true,
    consumerMix: true,
    assets: true,
};
