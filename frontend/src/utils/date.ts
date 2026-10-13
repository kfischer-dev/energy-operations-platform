export function formatDateTime(dateString: string) {
  const date = new Date(dateString);

  const datePart = date.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  });

  const timePart = date.toLocaleTimeString('de-DE', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return `${datePart} - ${timePart} Uhr`;
}