import { getImageProps } from "next/image";
import type { components } from "../../../../packages/contracts/schema";
import { EnquiryProvider } from "./QuickEnquiry";
import { JsonLd } from "./JsonLd";
import { referenceHtml } from "@/lib/reference-html.mjs";
import type { ReactNode } from "react";

type Block = components["schemas"]["ContentBlock"];

export function StructuredPage({
  blocks,
  slug,
}: {
  blocks: Block[];
  slug: string;
}) {
  const faqs: Block[] = [];
  let enquiries = false;
  function visit(items: Block[]) {
    for (const block of items) {
      if (block.kind === "faq") faqs.push(block);
      if (block.kind === "enquiry") enquiries = true;
      visit(block.children);
    }
  }
  visit(blocks);
  const preloads: ReactNode[] = [];
  const html = referenceHtml(blocks, {
    menu: slug === "menu",
    imageProps: (block, priority) => {
      const { props } = getImageProps({
        src: block.image,
        alt: block.alt,
        width: block.width,
        height: block.height,
        sizes: "(max-width: 767px) 92vw, (max-width: 1100px) 45vw, 600px",
        loading: priority ? "eager" : "lazy",
        fetchPriority: priority ? "high" : "auto",
      });
      if (priority)
        preloads.push(
          <link
            key={`${props.src}-${preloads.length}`}
            rel="preload"
            as="image"
            href={props.src}
            imageSrcSet={props.srcSet}
            imageSizes={props.sizes}
            fetchPriority="high"
          />,
        );
      return props;
    },
  });
  const page = (
    <>
      {preloads}
      {slug === "home" && (
        <JsonLd
          value={{
            "@context": "https://schema.org",
            "@type": "Organization",
            name: "Patnam Pakodi",
            url: "https://patnampakodi.com",
          }}
        />
      )}
      {faqs.length > 0 && (
        <JsonLd
          value={{
            "@context": "https://schema.org",
            "@type": "FAQPage",
            mainEntity: faqs.map((faq) => ({
              "@type": "Question",
              name: faq.title,
              acceptedAnswer: { "@type": "Answer", text: faq.text },
            })),
          }}
        />
      )}
      <div
        className={`reference-page reference-page-${slug}`}
        dangerouslySetInnerHTML={{
          __html: html,
        }}
      />
    </>
  );
  return enquiries ? <EnquiryProvider>{page}</EnquiryProvider> : page;
}
