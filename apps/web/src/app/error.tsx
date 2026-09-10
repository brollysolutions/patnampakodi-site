"use client";

export default function ErrorPage({ reset }: { reset: () => void }) {
  return (
    <section className="container empty-state not-found" role="alert">
      <h1>A little pause.</h1>
      <p>We couldn’t load the page. Please try again in a moment.</p>
      <button className="button button-primary" onClick={reset}>
        Try again
      </button>
    </section>
  );
}
