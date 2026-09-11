# Presenting the Patnam Pakodi store

Use a short shopping story to lead the presentation. Keep the technical details
for questions. Start with: “We kept Patnam Pakodi familiar and made the journey
from craving to checkout clear, on a phone or a desktop.”

## Prepare the demo

From the repository root, run:

```powershell
apps/api/.venv/Scripts/python.exe scripts/verify_staging.py --present
```

Docker must be running. The helper builds the current code, creates a separate
disposable Docker project, runs the checkout acceptance journey, then prints the
local demo URL and temporary admin sign-in details. Keep that terminal open.
Press Enter when finished; the helper removes only its own demo resources.

This demo uses clearly labelled synthetic products, stock, seller details and
delivery rules. Payments and messages use local provider fixtures: no money is
charged and no real message is sent. It does not populate the persistent review
site or production. Rehearse before the meeting; the first build takes time.

Use PIN **500001**, state **Telangana**, and an invented customer name/address.
Each fixture product costs ₹118; delivery costs ₹20. These are demonstration
values for reviewing the software, not proposed business prices.
The fresh fixture outlet is open throughout the week for a predictable demo.

Keep customer and administrator tabs separate. Use an incognito window for admin.
Use only the fixture credentials printed by the helper. Browser test screenshots
and HTML reports are retained under `apps/web/test-results/` and
`apps/web/playwright-report/`. The Docker demo screenshots are under
`apps/web/test-results-staging/`; these can support the presentation if a live
demonstration is interrupted.

## A ten-minute walkthrough

1. **The first impression — 1 minute.** Open the homepage. Point out the original
   logo, colours, Poppins and Inter, and reused food/packaging images. Show the
   equally visible fresh-food and packaged-product entrances. Resize to a phone.

2. **Finding something to order — 2 minutes.** Check delivery, browse a range,
   search or filter, and open a product. Show the price, portion or pack size,
   ingredients and allergens. Save a favourite, then add the item to the cart.
   Add something from the other mode and show that both baskets remain intact.

3. **Checkout — 2 minutes.** Open one basket, adjust quantity and continue.
   Enter the synthetic address. Review the itemised total and delivery fee.
   Fresh orders show their pilot outlet and preparation estimate. Continue to
   payment and choose “Pay securely”, then “Confirm test payment”.
   Refresh to show server-confirmed payment and the downloadable invoice.

4. **The customer after payment — 1 minute.** Show the private order link,
   progress timeline, invoice, support and order-again action. Explain that
   checkout is available without creating an account. Favourites stay on this
   browser. Customers can cancel fresh orders until preparation starts; staff can
   handle a later preparation cancellation without automatically restocking food.

5. **Running the store — 2 minutes.** In admin, show orders and the fresh
   “Start preparing” action, followed by dispatch and delivery. Open Delivery
   to show the pilot outlet, opening hours, pause switch and PIN fees.
   Show how the sticky sidebar or mobile tabs keep each area within reach. Order
   counts describe the current view; use Reports for date-based sales totals.
   Show product stock, enquiries, reports and media. Demonstrate
   changes only in this disposable demo.

6. **The rest of the brand — 1 minute.** Visit the story, branches, franchise,
   contact and any published policy pages. Show the brochure enquiry on a phone.
   These remain connected to the store and the shopping journey.

7. **Agree on activation — 1 minute.** Confirm the first outlet, products and
   delivery areas. Ask the client to review the experience as a buyer, then as
   the person operating orders.

Useful closing questions:

- Can a first-time buyer tell where to start without an explanation?
- Are the product names, images, portions and food information accurate?
- Can the operator handle a busy kitchen, unavailable stock and a customer query?
- Which pilot outlet and delivery PIN codes should be activated first?

## Confirm before taking real orders

Collect approved products, prices, stock, food facts, seller/invoice/tax details,
pilot outlet, PIN/state mappings, delivery fees, hours and preparation estimate.
Confirm customer support, cancellation/refund wording, named admin users and
who owns each operational task.

Live Razorpay capture/refund, WhatsApp consent/templates, production hosting,
backups, monitoring and deployment acceptance require the approved business
accounts and operator setup. Report the latest test and Lighthouse results from
the PR accurately; a local fixture payment is evidence of the implemented
workflow, not acceptance of a live payment account.

Keep the presentation focused on what is running. Do not promise instant
delivery, all-India service, live payments or performance results that have not
been verified.
