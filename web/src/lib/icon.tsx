import * as RiLib from 'react-icons/lib';
import codegen from "babel-plugin-codegen/macro";

// @ts-ignore
export const ALL_ICONS = RiLib['IconsManifest'];

// @ts-ignore
export const getIconById = (id) => {
  // @ts-ignore
  return ALL_ICONS.find((i) => i.id === id); // @ts-ignore
};


const fn = codegen`
const { IconsManifest } = require("react-icons/lib/cjs");

let codes = "(function (id) { switch (id) {";
IconsManifest.forEach(icon => {
  codes += 'case "' + icon.id + '":\\nreturn import("react-icons/' + icon.id +'/index");\\n'
})
codes += '}})';

module.exports = codes;
// module.exports = "import('react-icons/fa/index')"
`;

// @ts-ignore
export function getIcons(iconsId) {
  /*
  Dynamic Import with improved performance.
  Macros are used to avoid bundling unnecessary modules.

  Similar to this code
  ```
  return import(`react-icons/${iconsId}/index`);
  ```
  */

  return fn(iconsId);
}
