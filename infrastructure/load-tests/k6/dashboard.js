import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "1m", target: 10 },
    { duration: "3m", target: 30 },
    { duration: "1m", target: 0 },
  ],
  thresholds: {
    http_req_failed: ["rate<0.02"],
    http_req_duration: ["p(95)<3000"],
  },
};

const API = __ENV.API_URL || "http://localhost:8000";
const TOKEN = __ENV.ADMIN_JWT || "";

export default function dashboardTraffic() {
  const headers = TOKEN ? { Authorization: `Bearer ${TOKEN}` } : {};

  const ready = http.get(`${API}/api/v1/ready/`);
  check(ready, { "ready 200": (r) => r.status === 200 });

  const executive = http.get(`${API}/api/v1/analytics/admin/bi/snapshot/`, { headers });
  check(executive, {
    "bi snapshot auth or ok": (r) => r.status === 200 || r.status === 401 || r.status === 403,
  });

  const dashboard = http.get(`${API}/api/v1/analytics/admin/dashboard/`, { headers });
  check(dashboard, {
    "commerce dashboard": (r) => r.status === 200 || r.status === 401 || r.status === 403,
  });

  sleep(2);
}
