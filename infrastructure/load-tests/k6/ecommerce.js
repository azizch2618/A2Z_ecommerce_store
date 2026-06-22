/**
 * A2Z Tools — k6 load tests
 *
 * Install: https://k6.io/docs/get-started/installation/
 * Run:
 *   k6 run infrastructure/load-tests/k6/ecommerce.js
 *   k6 run infrastructure/load-tests/k6/api-throughput.js
 *   k6 run infrastructure/load-tests/k6/dashboard.js
 *
 * Override base URLs:
 *   k6 run -e API_URL=https://api.staging.a2ztools.com -e SITE_URL=https://staging.a2ztools.com ...
 */
import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "1m", target: 20 },
    { duration: "3m", target: 50 },
    { duration: "1m", target: 0 },
  ],
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<2000"],
  },
};

const API = __ENV.API_URL || "http://localhost:8000";
const SITE = __ENV.SITE_URL || "http://localhost:3000";

export default function ecommerceTraffic() {
  const home = http.get(`${SITE}/`);
  check(home, { "storefront home 200": (r) => r.status === 200 });

  const products = http.get(`${SITE}/products`);
  check(products, { "products page ok": (r) => r.status === 200 || r.status === 404 });

  const health = http.get(`${API}/api/v1/health/`);
  check(health, { "api health ok": (r) => r.status === 200 });

  sleep(1);
}
