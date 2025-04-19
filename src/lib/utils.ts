import { twMerge } from "tailwind-merge";

/**
 * It takes an array of strings, arrays, and objects, and returns a string of all the truthy values
 * @param args - array of strings, arrays, and objects
 * @returns a string of class names.
 */
export function cn(...args: C[]) {
  const result: string[] = [];

  for (let i = 0; i < args.length; i++) {
    const element = args[i];
    if (element == null || element === false || element === "") continue;

    if (typeof element === "string") {
      result.push(element);
    } else if (Array.isArray(element)) {
      const [cond, left, right = ""] = element;
      result.push(cond ? left : right);
    } else {
      for (const classes in element) {
        if (element[classes]) result.push(classes);
      }
    }
  }

  return twMerge(...result);
}

type C = undefined | null | false | string | [unknown, string, string?] | Record<string, unknown>;
