function isObject(item: any): boolean {
  return item && typeof item === 'object' && !Array.isArray(item);
}

function toCamel(s: string): string {
  return s.replace(/[_-][a-z]/g, (match) => match.charAt(1).toUpperCase());
}

export function convertKeysToCamel(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map((v) => convertKeysToCamel(v));
  } else if (isObject(obj)) {
    const newObj: any = {};
    Object.keys(obj).forEach((key) => {
      const newKey = toCamel(key);
      newObj[newKey] = convertKeysToCamel(obj[key]);
    });
    return newObj;
  }
  return obj;
}

export default convertKeysToCamel;
