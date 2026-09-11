import type { SVGProps } from "react";

const paths = {
  search: "m21 21-4.5-4.5 M19 10.5a8.5 8.5 0 1 1-17 0 8.5 8.5 0 0 1 17 0",
  refresh: "M20 7v5h-5 M4 17v-5h5 M6 6a8 8 0 0 1 13 3 M18 18a8 8 0 0 1-13-3",
  bag: "M5 7h14l1 14H4L5 7Z M8 8V6a4 4 0 0 1 8 0v2",
  heart:
    "M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z",
  pin: "M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z M15 10a3 3 0 1 1-6 0 3 3 0 0 1 6 0",
  arrow: "M4 12h16 m-6-6 6 6-6 6",
  chevron: "m9 5 7 7-7 7",
  close: "m6 6 12 12 M6 18 18 6",
  menu: "M4 6h16 M4 12h16 M4 18h16",
  home: "m3 10 9-7 9 7 M5 9v12h14V9 M9 21v-8h6v8",
  fresh:
    "M12 3c1 5 5 5 5 9a5 5 0 0 1-10 0c0-2 1-3 2-4 0 2 1 3 2 3 2 0 2-4 1-8Z M6 21h12",
  box: "m3 7 9-5 9 5v10l-9 5-9-5V7Z m0 0 9 5 9-5 M12 12v10 M7.5 4.5l9 5V14",
  truck:
    "M2 5h13v12H2V5Z M15 9h4l3 4v4h-7 M8 18a2 2 0 1 1-4 0 2 2 0 0 1 4 0 M20 18a2 2 0 1 1-4 0 2 2 0 0 1 4 0",
  clock: "M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0 M12 6v6l4 2",
  check: "m5 12 4 4L19 6",
  shield: "M12 2 3 6v6c0 5 9 10 9 10s9-5 9-10V6l-9-4Z m-4 10 3 3 5-6",
  plus: "M12 5v14 M5 12h14",
  minus: "M5 12h14",
  filter: "M4 6h16 M7 12h10 M10 18h4",
  phone: "M7 3H3c-1 10 8 19 18 18v-4l-5-2-2 2c-4-2-5-3-7-7l2-2-2-5Z",
  mail: "M3 5h18v14H3V5Z m0 0 9 8 9-8",
  chart: "M4 3v18h17 M8 16v-4 M13 16V7 M18 16v-7",
  settings: "M4 6h16 M4 18h16 M8 3v6 M16 15v6 M4 12h16 M13 9v6",
  image: "M3 3h18v18H3V3Z m0 14 5-5 4 4 3-3 6 6 M8 7h.01",
  document: "M5 2h9l5 5v15H5V2Z M14 2v6h5 M9 12h6 M9 16h6",
  users:
    "M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0 M5 22v-4a7 7 0 0 1 14 0v4 M2 10a3 3 0 0 1 2-5 M22 10a3 3 0 0 0-2-5",
} as const;
export type IconName = keyof typeof paths;
export function Icon({
  name,
  ...props
}: SVGProps<SVGSVGElement> & { name: IconName }) {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
      {...props}
    >
      <path d={paths[name]} />
    </svg>
  );
}
