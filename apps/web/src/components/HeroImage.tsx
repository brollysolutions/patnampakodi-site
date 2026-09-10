const sizes = "(max-width: 700px) 92vw, (max-width: 1100px) 46vw, 530px";
const sources = (format: string) =>
  [384, 750, 1122]
    .map((width) => `/generated/pakodi-${width}.${format} ${width}w`)
    .join(", ");

export function HeroImage({ priority = false }: { priority?: boolean }) {
  return (
    <figure className="hero-image">
      {priority && (
        <link
          rel="preload"
          as="image"
          type="image/avif"
          href="/generated/pakodi-750.avif"
          imageSrcSet={sources("avif")}
          imageSizes={sizes}
          fetchPriority="high"
        />
      )}
      <picture>
        <source type="image/avif" srcSet={sources("avif")} sizes={sizes} />
        {/* Build-time derivatives avoid a cold image-encoder request. */}
        <img
          src="/generated/pakodi-750.webp"
          srcSet={sources("webp")}
          sizes={sizes}
          alt="Illustration of golden chicken pakodi with curry leaves, chillies and lime"
          width={1122}
          height={1402}
          loading={priority ? "eager" : "lazy"}
          fetchPriority={priority ? "high" : "auto"}
          decoding="async"
        />
      </picture>
      <figcaption>Serving inspiration · illustration</figcaption>
    </figure>
  );
}
