import { ImageResponse } from "next/og";
import { readFile } from "node:fs/promises";
import { join } from "node:path";

export const alt = "Patnam Pakodi — Life Lo Spice Undali";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function OpenGraphImage() {
  const displayFont = await readFile(
    join(
      process.cwd(),
      "node_modules/@fontsource/abril-fatface/files/abril-fatface-latin-400-normal.woff",
    ),
  );
  return new ImageResponse(
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        width: "100%",
        height: "100%",
        background: "#FBEFD9",
        color: "#2B1406",
        padding: 80,
        justifyContent: "center",
        fontFamily: "Abril Fatface",
      }}
    >
      <div style={{ fontSize: 108, letterSpacing: -5 }}>Patnam Pakodi.</div>
      <div style={{ fontSize: 36, marginTop: 30 }}>Life Lo Spice Undali.</div>
      <div
        style={{
          display: "flex",
          width: 140,
          height: 10,
          background: "#EB6637",
          marginTop: 50,
        }}
      />
    </div>,
    {
      ...size,
      fonts: [
        {
          name: "Abril Fatface",
          data: displayFont,
          weight: 400,
          style: "normal",
        },
      ],
    },
  );
}
