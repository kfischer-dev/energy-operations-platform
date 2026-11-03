export function formatEnergy(kwh: number) {
  const absolute = Math.abs(kwh);

  let value = kwh;
  let unit = 'kWh';

  if (absolute >= 1_000_000) {
    value = kwh / 1_000_000;
    unit = 'GWh';
  } else if (absolute >= 1_000) {
    value = kwh / 1_000;
    unit = 'MWh';
  }

  return {
    value: Number(value.toFixed(2)),
    unit,
  };
}

export function formatPower(valueKw: number) {
  const abs = Math.abs(valueKw);

  if (abs >= 1_000_000) {
    return {
      value: Number((valueKw / 1_000_000).toFixed(2)),
      unit: 'GW',
    };
  }

  if (abs >= 1_000) {
    return {
      value: Number((valueKw / 1_000).toFixed(2)),
      unit: 'MW',
    };
  }

  return {
    value: Number(valueKw.toFixed(2)),
    unit: 'kW',
  };
}