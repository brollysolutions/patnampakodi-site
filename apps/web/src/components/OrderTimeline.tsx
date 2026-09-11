import { Icon } from "./Icon";
import type { Schema } from "@/lib/commerce";
export function OrderTimeline({ order }: { order: Schema["OrderView"] }) {
  const steps =
    order.shopping_mode === "fresh"
      ? [
          ["approved", "Order reviewed"],
          ["paid", "Payment confirmed"],
          ["preparing", "Preparing"],
          ["dispatched", "Out for delivery"],
          ["delivered", "Delivered"],
        ]
      : [
          ["approved", "Order reviewed"],
          ["paid", "Payment confirmed"],
          ["dispatched", "Dispatched"],
          ["delivered", "Delivered"],
        ];
  const status =
    order.status === "payment_pending"
      ? "approved"
      : order.status === "delivery_issue"
        ? "dispatched"
        : order.status;
  const current = steps.findIndex(([key]) => key === status);
  if (current < 0) return null;
  return (
    <ol className="order-timeline" aria-label="Order progress">
      {steps.map(([key, label], index) => (
        <li
          key={key}
          className={index <= current ? "is-done" : ""}
          aria-current={index === current ? "step" : undefined}
        >
          <span>{index < current ? <Icon name="check" /> : index + 1}</span>
          <div>
            {label}
            {index === current && (
              <small>
                {order.status === "payment_pending"
                  ? "Waiting for payment confirmation"
                  : order.status === "delivery_issue"
                    ? "Our team is checking delivery"
                    : "Current stage"}
              </small>
            )}
          </div>
        </li>
      ))}
    </ol>
  );
}
