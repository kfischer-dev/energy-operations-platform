import type { AssetResponse } from '../types/assets';
import './AssetOverview.css';

type AssetOverviewProps = {
  assets: AssetResponse[];
};

function formatAssetType(value: string): string {
  return value
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export function AssetOverview({ assets }: AssetOverviewProps) {
  return (
    <section className="asset-overview">
      <div className="asset-overview-header">
        <div>
          <h2>Asset Overview</h2>
          <p>Registered energy assets</p>
        </div>
        <span className="asset-overview-count">{assets.length} assets</span>
      </div>

      {assets.length === 0 ? (
        <p className="asset-overview-empty">No assets available.</p>
      ) : (
        <div className="asset-overview-table-wrap">
          <table className="asset-overview-table">
            <thead>
              <tr>
                <th scope="col">Asset</th>
                <th scope="col">Type</th>
                <th scope="col">Role</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((asset) => (
                <tr key={asset.asset_id}>
                  <td>{asset.asset_name}</td>
                  <td>{formatAssetType(asset.asset_type)}</td>
                  <td>
                    <span className={`asset-overview-role asset-overview-role--${asset.asset_role}`}>
                      {asset.asset_role === 'producer' ? 'Producer' : 'Consumer'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
