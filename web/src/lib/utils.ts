export function capitalize(x: string): string {
  const firstChar = x.charAt(0).toUpperCase();
  const remainingChars = x.slice(1);
  return `${firstChar}${remainingChars}`;
}
