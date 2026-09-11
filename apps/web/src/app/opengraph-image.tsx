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
      "node_modules/@fontsource/poppins/files/poppins-latin-700-normal.woff",
    ),
  );
  return new ImageResponse(
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        width: "100%",
        height: "100%",
        background: "#FEF1E4",
        color: "#1C1C1C",
        padding: 80,
        justifyContent: "center",
        fontFamily: "Poppins",
        fontWeight: 700,
      }}
    >
      <div style={{ fontSize: 100, letterSpacing: -3 }}>Patnam Pakodi.</div>
      <div style={{ fontSize: 36, marginTop: 30 }}>Life Lo Spice Undali.</div>
      <div
        style={{
          display: "flex",
          width: 140,
          height: 10,
          background: "#FF6210",
          marginTop: 50,
        }}
      />
    </div>,
    {
      ...size,
      fonts: [
        {
          name: "Poppins",
          data: displayFont,
          weight: 700,
          style: "normal",
        },
      ],
    },
  );
}
