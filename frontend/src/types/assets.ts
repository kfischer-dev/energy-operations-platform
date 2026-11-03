export type OperatingStatus =
  | 'online'
  | 'offline'
  | 'maintenance'
  | 'fault';

export type AssetResponse = {
  asset_id: number;
  asset_name: string;
  asset_code: string;
  asset_location: string;
  asset_role: string;
  asset_type: string;
  region_id: number;
  region_code: string;
  region_name: string;
  rated_power_kw: number;
  latitude: number;
  longitude: number;
  operating_status: OperatingStatus;
};